"""The "Mu + Lambda" Simplification Modification

This module defines the basis of the "mu plus lambda"
evolutionary algorithm in bingo analyses with an added simplification component.
The next generation is evaluated and selected from both the parent and offspring
populations, along with a fixed number of simplified equations based on the same.
"""
from .evolutionary_algorithm import EvolutionaryAlgorithm
from ..variation.var_or import VarOr
from ..simplification.simplification import Simplification
from ..selection.tournament import Tournament


class MuPlusLambdaSimplified(EvolutionaryAlgorithm):
    """The algorithm used to perform generational steps.

    A class for the "mu plus lambda" evolutionary algorithm in bingo.

    Parameters
    ----------
    evaluation : evaluation
        The evaluation algorithm that sets the fitness on the population.
    selection : selection
        selection instance to perform selection on a population
    crossover : Crossover
        The algorithm that performs crossover during variation.
    mutation : Mutation
        The algorithm that performs mutation during variation.
    crossover_probability : float
        Probability that crossover will occur on an individual.
    mutation_probability : float
        Probability that mutation will occur on an individual.
    number_offspring : int
        The number of offspring produced from variation.
    target_population_size : int (optional)
        The targeted population size. Default is to keep the population the
        same size as the starting population

    Attributes
    ----------
    variation : VarOr
                VarOr variation to perform variation on a population
    evaluation : evaluation
                 evaluation instance to perform evaluation on a population
    selection : selection
                selection instance to perform selection on a population
    """
    def __init__(self, evaluation, crossover, mutation,
                 crossover_probability, mutation_probability,
                 number_offspring, target_population_size=None, simplified_population_size=10, tournament_selection_size=20):
        super().__init__(variation=VarOr(crossover, mutation,
                                         crossover_probability,
                                         mutation_probability),
                         evaluation=evaluation,
                         selection=Tournament(tournament_size=tournament_selection_size))
        self.simplification = Simplification()
        self._number_offspring = number_offspring
        self._target_populations_size = target_population_size
        self._simplified_population_size = simplified_population_size

    def generational_step(self, population):
        """Performs selection on individuals.

        Parameters
        ----------
        population : list of chromosomes
                     The population at the start of the generational step

        Returns
        -------
        list of chromosomes :
            The next generation of the population
        """
        variation_offspring = self.variation(population, self._number_offspring)
        simplified_offspring = self.simplification(population, self._simplified_population_size)
        self.evaluation(population + variation_offspring + simplified_offspring)
        if self._target_populations_size is None:
            new_pop_size = len(population)
        else:
            new_pop_size = self._target_populations_size
        return self.selection(population + variation_offspring + simplified_offspring, new_pop_size)
