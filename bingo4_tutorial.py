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
STACK_SIZE = 10
MAX_GENERATIONS = 30000
FITNESS_THRESHOLD = 1e-4
STAGNATION_LIMIT = 10000
MIN_GENERATIONS = 50


def init_x_vals(start, stop, num_points):
  return np.linspace(start, stop, num_points).reshape([-1, 1])


def equation_eval(x):
  return x**2 + 3.5*x**3


def execute_generational_steps():
  communicator = MPI.COMM_WORLD
  rank = MPI.COMM_WORLD.Get_rank()

  data = pd.read_csv('../genetic-prog-data/F_data/CSV/RajuNewman/fp_2var_test9_py.csv').as_matrix()
  x = data[:,0:2]
  y = data[:2]

  if rank == 0:
    x = init_x_vals(-10, 10, 100)
    y = equation_eval(x)

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
  execute_generational_steps()


if __name__ == '__main__':
  main()
