# Ignoring some linting rules in tests
# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring
import numpy as np
import pandas as pd
from mpi4py import MPI

from bingo.symbolic_regression.agraph.crossover import AGraphCrossover
from bingo.symbolic_regression.agraph.mutation import AGraphMutation
from bingo.symbolic_regression.agraph.generator import AGraphGenerator
from bingo.symbolic_regression.agraph.component_generator \
  import ComponentGenerator
from bingo.symbolic_regression.explicit_regression \
  import ExplicitRegression, ExplicitTrainingData

from bingo.evolutionary_algorithms.deterministic_crowding import DeterministicCrowdingEA
from bingo.evolutionary_algorithms.age_fitness import AgeFitnessEA
from bingo.evolutionary_optimizers.parallel_archipelago \
  import ParallelArchipelago
from bingo.evaluation.evaluation import Evaluation
from bingo.evolutionary_optimizers.island import Island
from bingo.local_optimizers.continuous_local_opt \
  import ContinuousLocalOptimization

from bingo.util import log
log.configure_logging(verbosity='detailed',module=True,timestamp=False,stats_file='stats.log')

POP_SIZE = 3000
STACK_SIZE = 20
MAX_GENERATIONS = 30000
FITNESS_THRESHOLD = 1e-4
STAGNATION_LIMIT = 30000
MIN_GENERATIONS = 50
PATH = './data/fp_1var_test1.csv'

def execute_generational_steps():
  communicator = MPI.COMM_WORLD
  rank = MPI.COMM_WORLD.Get_rank()

  data = pd.read_csv(PATH).as_matrix()
  x = data[:,0:1]
  y = data[:1]

  x = MPI.COMM_WORLD.bcast(x, root=0)
  y = MPI.COMM_WORLD.bcast(y, root=0)

  training_data = ExplicitTrainingData(x, y)

  component_generator = ComponentGenerator(x.shape[1])
  component_generator.add_operator(2)
  component_generator.add_operator(3)
  component_generator.add_operator(4)
  component_generator.add_operator(5)
  component_generator.add_operator(6)
  component_generator.add_operator(7)
  component_generator.add_operator(10)

  crossover = AGraphCrossover(component_generator)
  mutation = AGraphMutation(component_generator)

  agraph_generator = AGraphGenerator(STACK_SIZE, component_generator)

  fitness = ExplicitRegression(training_data=training_data, metric='root mean squared error')
  local_opt_fitness = ContinuousLocalOptimization(fitness, algorithm='L-BFGS-B')
  evaluator = Evaluation(local_opt_fitness)

  #ea = AgeFitnessEA(evaluator, agraph_generator, crossover,
  #          mutation, 0.4, 0.4, POP_SIZE)

  ea = DeterministicCrowdingEA(evaluator, crossover, mutation, 0.4, 0.4)
  island = Island(ea, agraph_generator, POP_SIZE)

  archipelago = ParallelArchipelago(island)

  opt_result = archipelago.evolve_until_convergence(MAX_GENERATIONS,
                            fitness_threshold=FITNESS_THRESHOLD, min_generations=MIN_GENERATIONS, stagnation_generations=STAGNATION_LIMIT)
  if opt_result.success:
    if rank == 0:
      print("best: ", archipelago.get_best_individual())


def main():
  print("Executing base test with:\n  STACK_SIZE =", STACK_SIZE, "\n  POP_SIZE =", POP_SIZE, "\n  MIN_GENERATIONS =", MIN_GENERATIONS, "\n  MAX_GENERATIONS =", MAX_GENERATIONS, "\n  FITNESS_THRESHOLD =", FITNESS_THRESHOLD, "\n  PATH =", PATH)

  execute_generational_steps()


if __name__ == '__main__':
  main()
  
