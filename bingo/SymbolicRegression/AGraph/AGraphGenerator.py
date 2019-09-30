"""Generator of acyclic graph individuals.

This module contains the implementation of the generation of random acyclic
graph individuals.
"""
import numpy as np

from .AGraph import AGraph, COMMAND_ARRAY_DTYPE
from ...Base.Generator import Generator
from ...Util.ArgumentValidation import argument_validation


class AGraphGenerator(Generator):
    """Generates acyclic graph individuals

    Parameters
    ----------
    agraph_size : int
                  command array size of the generated acyclic graphs
    component_generator : AGraph.ComponentGenerator
                          Generator of stack components of agraphs
    """
    @argument_validation(agraph_size={">=": 1})
    def __init__(self, agraph_size, component_generator):
        self.agraph_size = agraph_size
        self.component_generator = component_generator
        self._manual_constants = \
            not component_generator.automatic_constant_optimization

    def __call__(self):
        """Generates random agraph individual.

        Fills stack based on random commands from the component generator.

        Returns
        -------
        Agraph
            new random acyclic graph individual
        """
        individual = AGraph()
        individual.command_array = self._create_command_array()
        if self._manual_constants:
            self._insert_manual_constants(individual)
        return individual

    def _create_command_array(self):
        command_array = np.empty((self.agraph_size, 3),
                                 dtype=COMMAND_ARRAY_DTYPE)
        for i in range(self.agraph_size):
            command_array[i] = self.component_generator.random_command(i)
        return command_array

    def _insert_manual_constants(self, individual):
        for i in individual.find_inserted_constants():
            individual.constants[i] = \
                self.component_generator.random_numerical_constant()
