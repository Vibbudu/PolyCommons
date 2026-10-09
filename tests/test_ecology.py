"""Unit tests for ecological dynamics and tipping point behavior."""

import pytest
import numpy as np
from polycommons.config import EcologyConfig
from polycommons.ecology import ResourceStock


def test_resource_logistic_growth():
    """Verify that resource grows toward carrying capacity in the absence of harvest."""
    config = EcologyConfig(
        carrying_capacity=1000.0,
        regeneration_rate=0.2,
        tipping_threshold=100.0,
        initial_stock=500.0,
        stochastic_shock_std=0.0,
    )
    res = ResourceStock(config, seed=42)
    zero_harvests = np.zeros(10)

    for _ in range(50):
        res.harvest_and_step(zero_harvests)

    assert res.stock > 500.0
    assert res.stock <= config.carrying_capacity
    assert np.isclose(res.stock, config.carrying_capacity, atol=20.0)


def test_tipping_point_collapse():
    """Verify that when stock falls below tipping threshold, regeneration is suppressed."""
    config = EcologyConfig(
        carrying_capacity=1000.0,
        regeneration_rate=0.2,
        tipping_threshold=300.0,
        tipping_steepness=0.1,
        initial_stock=100.0,  # Below tipping point
        stochastic_shock_std=0.0,
    )
    res = ResourceStock(config, seed=42)
    growth_sub = res.ecological_regeneration(100.0)
    growth_super = res.ecological_regeneration(600.0)

    # Growth below threshold should be heavily curtailed compared to above
    assert growth_sub < 0.1 * growth_super


def test_harvest_conservation_and_rationing():
    """Verify that harvest never extracts more stock than available."""
    config = EcologyConfig(
        carrying_capacity=1000.0,
        regeneration_rate=0.0,
        tipping_threshold=0.0,
        initial_stock=50.0,
        stochastic_shock_std=0.0,
    )
    res = ResourceStock(config, seed=42)
    
    # Request massive extraction exceeding available stock
    excessive_harvest = np.array([100.0, 100.0])
    realized = res.harvest_and_step(excessive_harvest)

    assert np.sum(realized) <= 50.0001
    assert res.stock >= 0.0
