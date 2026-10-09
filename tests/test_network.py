"""Unit tests for network generation, metrics, and dynamic ostracism rewiring."""

import pytest
import networkx as nx
from polycommons.config import NetworkConfig
from polycommons.network import SocialNetwork


def test_network_topologies_generation():
    """Verify that small_world, scale_free, and stochastic_block topologies build valid graphs."""
    for topo in ["small_world", "scale_free", "stochastic_block", "random_regular"]:
        cfg = NetworkConfig(topology=topo, n_communities=3, k_neighbors=4)
        net = SocialNetwork(n_agents=30, config=cfg, seed=42)
        assert net.graph.number_of_nodes() == 30
        assert net.graph.number_of_edges() > 0
        assert not any(u == v for u, v in net.graph.edges())


def test_ostracism_rewiring():
    """Verify that rewiring severs edge with defector and establishes new edge to cooperator."""
    cfg = NetworkConfig(topology="small_world", k_neighbors=2)
    net = SocialNetwork(n_agents=5, config=cfg, seed=42)

    # Force an edge between agent 0 (cooperator) and 1 (defector)
    net.graph.add_edge(0, 1)
    cooperators = [0, 2, 3]

    # Rewire with probability 1.0
    rewired = net.rewire_ostracism(
        agent_id=0,
        target_defector_id=1,
        cooperator_ids=cooperators,
        rewire_prob=1.0,
    )

    assert rewired is True
    assert not net.graph.has_edge(0, 1)
    assert net.graph.has_edge(0, 2) or net.graph.has_edge(0, 3)
