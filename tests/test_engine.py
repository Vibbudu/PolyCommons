"""Unit tests for the PolyCommons simulation engine."""

import pytest
import numpy as np
from polycommons.config import (
    SimulationConfig,
    EcologyConfig,
    AgentConfig,
    NetworkConfig,
    GovernanceConfig,
)
from polycommons.engine import PolyCommonsSim


def test_simulation_run_steps():
    """Verify that simulation runs for specified steps and logs expected trajectory columns."""
    cfg = SimulationConfig(
        n_steps=10,
        agents=AgentConfig(n_agents=20),
        ecology=EcologyConfig(initial_stock=500.0),
        governance=GovernanceConfig(regime="open_access"),
        seed=42,
    )
    sim = PolyCommonsSim(cfg)
    df = sim.run()

    assert len(df) == 10
    assert "cooperation_rate" in df.columns
    assert "resource_stock" in df.columns
    assert "gini_wealth" in df.columns
    assert "sanction_events" in df.columns
    assert df["resource_stock"].min() >= 0.0


def test_simulation_shock():
    """Verify that external shock decreases resource stock."""
    cfg = SimulationConfig(
        n_steps=10,
        agents=AgentConfig(n_agents=20),
        ecology=EcologyConfig(initial_stock=500.0),
        governance=GovernanceConfig(regime="polycentric"),
        seed=42,
    )
    sim = PolyCommonsSim(cfg)
    df = sim.run_with_shock(shock_step=5, shock_magnitude=200.0)

    assert len(df) == 10
    # Stock after shock should be lower
    assert df.loc[5, "resource_stock"] < df.loc[4, "resource_stock"]
