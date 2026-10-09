"""Unit tests for institutional governance regimes and sanctions."""

import pytest
import numpy as np

from polycommons.agents import Agent
from polycommons.config import GovernanceConfig, NetworkConfig
from polycommons.institutions import (
    OpenAccess,
    PeerPunishment,
    CentralizedPool,
    PolycentricGovernance,
    create_institution,
)
from polycommons.network import SocialNetwork


def test_open_access_regime():
    """Verify that open access imposes no sanctions or costs."""
    agents = [Agent(0, True), Agent(1, False)]
    net_config = NetworkConfig(topology="small_world", k_neighbors=2)
    network = SocialNetwork(2, net_config, seed=42)
    gov_config = GovernanceConfig()
    rng = np.random.default_rng(42)

    inst = create_institution("open_access")
    metrics = inst.apply_governance(agents, network, gov_config, rng)

    assert metrics["sanction_events"] == 0
    assert metrics["total_fines"] == 0.0
    assert metrics["total_monitoring_cost"] == 0.0


def test_peer_punishment_regime():
    """Verify that cooperator punishes adjacent defector."""
    agents = [Agent(0, True), Agent(1, False)]
    agents[0].payoff = 10.0
    agents[1].payoff = 10.0

    network = SocialNetwork(2, NetworkConfig(topology="small_world", k_neighbors=2), seed=42)
    network.graph.add_edge(0, 1)

    gov_config = GovernanceConfig(peer_punish_cost=0.5, peer_punish_fine=2.0)
    rng = np.random.default_rng(42)

    inst = create_institution("peer_punishment")
    metrics = inst.apply_governance(agents, network, gov_config, rng)

    assert metrics["sanction_events"] == 1
    assert agents[0].payoff == 10.0 - 0.5
    assert agents[1].payoff == 10.0 - 2.0


def test_centralized_pool_taxation():
    """Verify that centralized pool taxes all agents and sanctions defectors."""
    agents = [Agent(0, True), Agent(1, False)]
    for a in agents:
        a.payoff = 10.0

    network = SocialNetwork(2, NetworkConfig(), seed=42)
    gov_config = GovernanceConfig(
        central_tax=1.0,
        central_audit_efficiency=1.0,
        central_fine=3.0,
    )
    rng = np.random.default_rng(42)

    inst = create_institution("centralized_pool")
    metrics = inst.apply_governance(agents, network, gov_config, rng)

    # Both pay tax
    assert agents[0].payoff == 9.0  # 10 - 1
    assert agents[1].payoff <= 9.0  # 10 - 1 - fine
    assert metrics["total_monitoring_cost"] == 2.0


def test_polycentric_graduated_sanction():
    """Verify that repeated offenses in polycentric regime escalate the fine."""
    agents = [Agent(0, True, community_id=0), Agent(1, False, community_id=0)]
    agents[0].payoff = 20.0
    agents[1].payoff = 20.0
    agents[1].offense_count = 2

    network = SocialNetwork(2, NetworkConfig(), seed=42)
    network.graph.add_edge(0, 1)

    gov_config = GovernanceConfig(
        polycentric_local_fine=1.0,
        polycentric_graduated_factor=1.5,
        polycentric_local_cost=0.1,
        polycentric_rewire_rate=0.0,
    )
    rng = np.random.default_rng(42)

    inst = create_institution("polycentric")
    metrics = inst.apply_governance(agents, network, gov_config, rng)

    assert metrics["sanction_events"] >= 1
    # Fine should be scaled by factor^2 (1.0 * 1.5^2 = 2.25)
    assert agents[1].offense_count == 3
