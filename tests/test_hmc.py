import numpy as np
import numpy.testing as npt

import littlemcmc as lmc
from littlemcmc import HamiltonianMC
from test_utils import logp_dlogp_func
import pytest
import logging


def test_leapfrog_reversible():
    np.random.seed(42)
    size = 1
    scaling = np.random.rand(size)
    step = HamiltonianMC(logp_dlogp_func=logp_dlogp_func, size=size, scaling=scaling)
    p = step.potential.random()
    q = np.random.randn(size)
    start = step.integrator.compute_state(p, q)

    for epsilon in [0.01, 0.1]:
        for n_steps in [1, 2, 3, 4, 20]:
            state = start
            for _ in range(n_steps):
                state = step.integrator.step(epsilon, state)
            for _ in range(n_steps):
                state = step.integrator.step(-epsilon, state)
            npt.assert_allclose(state.q, start.q, rtol=1e-5)
            npt.assert_allclose(state.p, start.p, rtol=1e-5)


def test_nuts_tuning():
    size = 1
    stepper = lmc.NUTS(logp_dlogp_func=logp_dlogp_func, size=size)
    draws = 5
    tune = 5
    chains = 1
    cores = 1
    trace, stats = lmc.sample(
        logp_dlogp_func, size, stepper, draws, tune, chains=chains, cores=cores
    )

    assert not stepper.tune
    # FIXME revisit this test once trace object has been stabilized.
    # assert np.all(trace['step_size'][5:] == trace['step_size'][5])