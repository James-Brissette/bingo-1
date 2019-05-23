# Ignoring some linting rules in tests
# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring
import pytest

from bingo.Base.EvolutionaryOptimizer import EvolutionaryOptimizer


class DummyEO(EvolutionaryOptimizer):
    def __init__(self, convergence_rate):
        self.best_fitness = 1.0
        self.convergence_rate = convergence_rate
        super().__init__()

    def evolve(self, num_generations):
        self.best_fitness *= self.convergence_rate
        self.generational_age += num_generations

    def get_best_fitness(self):
        return self.best_fitness

    def get_best_individual(self):
        return [self.best_fitness]

    def get_fitness_evaluation_count(self):
        return self.generational_age * 2


@pytest.fixture
def converging_eo():
    return DummyEO(0.5)


@pytest.fixture
def stale_eo():
    return DummyEO(1.0)


def test_run_until_absolute_convergence(converging_eo):
    optimization_result = \
        converging_eo.evolve_until_convergence(max_generations=10,
                                               convergence_check_frequency=1,
                                               fitness_threshold=0.126,
                                               stagnation_generations=10)
    assert optimization_result.success
    assert optimization_result.status == 0
    assert optimization_result.ngen == 3
    assert pytest.approx(optimization_result.fitness, 0.125)


def test_run_min_generations_converge(converging_eo):
    optimization_result = \
        converging_eo.evolve_until_convergence(max_generations=10,
                                               min_generations=25,
                                               convergence_check_frequency=1,
                                               fitness_threshold=0.126,
                                               stagnation_generations=10)
    assert optimization_result.status == 0
    assert optimization_result.ngen == 25


def test_run_min_generations_stagnate(stale_eo):
    optimization_result = \
        stale_eo.evolve_until_convergence(max_generations=10,
                                          min_generations=25,
                                          convergence_check_frequency=1,
                                          fitness_threshold=0.126,
                                          stagnation_generations=10)
    assert optimization_result.status == 1
    assert optimization_result.ngen == 25


def test_num_gens_taken_in_optimization(converging_eo):
    optimization_result = \
        converging_eo.evolve_until_convergence(max_generations=10,
                                               convergence_check_frequency=1,
                                               fitness_threshold=0.26,
                                               stagnation_generations=10)
    assert optimization_result.ngen == 2
    optimization_result = \
        converging_eo.evolve_until_convergence(max_generations=10,
                                               convergence_check_frequency=1,
                                               fitness_threshold=0.126,
                                               stagnation_generations=10)
    assert optimization_result.ngen == 1


def test_run_convergence_check_chunks(converging_eo):
    optimization_result = \
        converging_eo.evolve_until_convergence(max_generations=100,
                                               convergence_check_frequency=5,
                                               fitness_threshold=0.126,
                                               stagnation_generations=10)
    assert optimization_result.ngen == 15


def test_run_until_stagnation(stale_eo):
    optimization_result = \
        stale_eo.evolve_until_convergence(max_generations=10,
                                          convergence_check_frequency=1,
                                          fitness_threshold=0.126,
                                          stagnation_generations=5)
    assert not optimization_result.success
    assert optimization_result.status == 1
    assert optimization_result.ngen == 5
    assert pytest.approx(optimization_result.fitness, 1.0)


def test_run_until_max_steps(converging_eo):
    optimization_result = \
        converging_eo.evolve_until_convergence(max_generations=2,
                                               convergence_check_frequency=1,
                                               fitness_threshold=0.126)
    assert not optimization_result.success
    assert optimization_result.status == 2
    assert optimization_result.ngen == 2
    assert pytest.approx(optimization_result.fitness, 0.25)


@pytest.mark.parametrize("min_generations", [0, 2])
def test_run_until_max_fitness_evaluations(converging_eo, min_generations):
    optimization_result = \
        converging_eo.evolve_until_convergence(max_generations=10,
                                               min_generations=min_generations,
                                               convergence_check_frequency=1,
                                               fitness_threshold=0.126,
                                               max_fitness_evaluations=4)
    assert not optimization_result.success
    assert optimization_result.status == 3
    assert optimization_result.ngen == 2
    assert pytest.approx(optimization_result.fitness, 0.25)


@pytest.mark.parametrize('invalid_arg_dict',
                         [{'max_generations': 0},
                          {'convergence_check_frequency': 0},
                          {'min_generations': -1}])
def test_raises_error_on_invalid_input(converging_eo, invalid_arg_dict):
    arg_dict = {'max_generations': 2,
                'convergence_check_frequency': 1,
                'absolute_error_threshold': 0.126,
                'stagnation_generations': 10,
                'min_generations': 0}
    arg_dict.update(invalid_arg_dict)
    with pytest.raises(ValueError):
        _ = converging_eo.evolve_until_convergence(**arg_dict)