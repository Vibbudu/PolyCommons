"""Quantitative metrics and analytical tools for socio-ecological dilemma dynamics."""

from typing import Dict, List
import numpy as np
import networkx as nx

from polycommons.agents import Agent
from polycommons.network import SocialNetwork


def compute_cooperation_rate(agents: List[Agent]) -> float:
    """Calculates the proportion of cooperative agents in the population."""
    if not agents:
        return 0.0
    return float(sum(1 for a in agents if a.is_cooperator) / len(agents))


def compute_gini_coefficient(values: np.ndarray) -> float:
    """Computes the Gini coefficient measuring inequality in wealth or payoffs.
    
    Returns a value in [0, 1], where 0 is perfect equality and 1 is maximum inequality.
    """
    v = np.asarray(values, dtype=float)
    if v.size == 0:
        return 0.0

    # Shift values if negative so all entries are non-negative for Gini
    min_val = np.min(v)
    if min_val < 0:
        v = v - min_val

    total = np.sum(v)
    if total <= 1e-9:
        return 0.0

    v_sorted = np.sort(v)
    n = len(v)
    index = np.arange(1, n + 1)
    gini = (2.0 * np.sum(index * v_sorted) - (n + 1) * total) / (n * total)
    return float(np.clip(gini, 0.0, 1.0))


def compute_assortativity_cooperation(agents: List[Agent], network: SocialNetwork) -> float:
    """Calculates the fraction of edges connecting two cooperators (network reciprocity metric)."""
    edges = network.graph.edges()
    total_edges = len(edges)
    if total_edges == 0:
        return 0.0

    cc_count = 0
    for u, v in edges:
        if agents[u].is_cooperator and agents[v].is_cooperator:
            cc_count += 1

    return float(cc_count / total_edges)


def compute_step_summary(
    agents: List[Agent],
    network: SocialNetwork,
    resource_stock: float,
    carrying_capacity: float,
    governance_metrics: Dict[str, float],
) -> Dict[str, float]:
    """Summarizes systemic indicators at the current time step."""
    payoffs = np.array([a.payoff for a in agents])
    wealths = np.array([a.wealth for a in agents])

    coop_rate = compute_cooperation_rate(agents)
    gini_wealth = compute_gini_coefficient(wealths)
    gini_payoff = compute_gini_coefficient(payoffs)
    cc_assortativity = compute_assortativity_cooperation(agents, network)
    net_metrics = network.network_metrics()

    return {
        "cooperation_rate": coop_rate,
        "resource_stock": resource_stock,
        "resource_fraction": resource_stock / max(1e-5, carrying_capacity),
        "mean_payoff": float(np.mean(payoffs)),
        "std_payoff": float(np.std(payoffs)),
        "mean_wealth": float(np.mean(wealths)),
        "gini_wealth": gini_wealth,
        "gini_payoff": gini_payoff,
        "cc_assortativity": cc_assortativity,
        "avg_degree": net_metrics["avg_degree"],
        "clustering_coef": net_metrics["clustering_coef"],
        "sanction_events": governance_metrics.get("sanction_events", 0.0),
        "total_fines": governance_metrics.get("total_fines", 0.0),
        "total_monitoring_cost": governance_metrics.get("total_monitoring_cost", 0.0),
        "rewire_events": governance_metrics.get("rewire_events", 0.0),
    }
