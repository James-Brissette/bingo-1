"""simplification of subset of passed in population

simplification.py relies on the stackGenerator class to reconstruct a DAG
from a string representation of a string output sourced from sympy's simplify()
function
"""
import numpy as np
import random

from .stackgenerator import stackGenerator
from ..util.argument_validation import argument_validation
#from ..symbolic_regression.agraph.agraph import get_simple_sympy_string, _get_formatted_string_using, _get_formatted_element_string
#from ..symbolic_regression.agraph.maps import CONSOLE_PRINT_MAP


class Simplification():
    """variation where crossover and mutation may co-occur

    Parameters
    ----------
    crossover : Crossover
                Crossover function class used in the variation
    mutation : Mutation
               Mutation function class used in the variation
    crossover_probability : float
                            Probability that crossover will occur on an
                            individual
    mutation_probability : float
                           Probability that mutation will occur on an individual


    Attributes
    ----------
    simplification_offspring : array of bool
                          list indicating whether the corresponding member of
                          the last offspring was a result of simplification
    """


    @argument_validation(number_offspring={">=": 0})
    def __call__(self, population, number_offspring):
        """Performs simplification variation on a population.

        Parameters
        ----------
        population : list of chromosomes
                     The population on which to perform selection
        number_offspring : int
                           number of offspring to produce

        Returns
        -------
        list of chromosomes :
            The offspring of the population
        """
        self.simplification_offspring = np.zeros(number_offspring, bool)
        offspring = self._simplify_population(population, number_offspring)
        return offspring

    def _simplify_population(self, population, number_offspring):
        offspring = []
        #Randomly select number_offspring chromosomes from population
        for idx in random.sample(range(len(population)),number_offspring):
            #DEEP_COPY of original expression
            #self.simplification_offspring[idx] = True
            chromosome = population[idx].__deepcopy__()

            #Generate Sympy string & Simplify, then Reconstruct DAG from simplified expression
            generator = stackGenerator()
            generator.generateDAG(chromosome.get_simple_sympy_string().replace("?","1"))
            
            #Distribute DAG into DEEP_COPY of original expression
            if (len(generator.stack) <= len(chromosome._command_array)):
                chromosome._command_array = generator.distributeArray(chromosome._command_array, generator.stack)
                chromosome._constants = generator.constantStack
            else:
                print("Simplified Stack exceeded length of original")
        
            offspring.append(chromosome)
            #Track number of errors
        
        #Return simplified population
        return offspring
    
    
