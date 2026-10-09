"""Institutional governance mechanisms: Open Access, Peer Sanction, Centralized Pool, and Polycentric."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np

from polycommons.agents import Agent
from polycommons.config import GovernanceConfig
from polycommons.network import SocialNetwork


class BaseInstitution(ABC):
    """Abstract base class for governance mechanisms in common-pool dilemmas."""

    @abstractmethod
    def apply_governance(
        self,
        agents: List[Agent],
        network: SocialNetwork,
        config: GovernanceConfig,
        rng: np.random.Generator,
    ) -> Dict[str, float]:
        """Applies monitoring, taxes, sanctions, and network interventions.
        
        Returns:
            Dictionary of governance metrics (sanctions count, total fines, etc.)
        """
        pass


class OpenAccess(BaseInstitution):
    """Unregulated open-access regime with zero monitoring and zero sanctions."""

    def apply_governance(
        self,
        agents: List[Agent],
        network: SocialNetwork,
        config: GovernanceConfig,
        rng: np.random.Generator,
    ) -> Dict[str, float]:
        return {
            "sanction_events": 0.0,
            "total_fines": 0.0,
            "total_monitoring_cost": 0.0,
            "rewire_events": 0.0,
        }


class PeerPunishment(BaseInstitution):
    """Decentralized peer sanctioning where cooperators punish defector neighbors."""

    def apply_governance(
        self,
        agents: List[Agent],
        network: SocialNetwork,
        config: GovernanceConfig,
        rng: np.random.Generator,
    ) -> Dict[str, float]:
        sanctions_count = 0
        total_fines = 0.0
        total_costs = 0.0

        for agent in agents:
            if not agent.is_cooperator:
                continue

            neighbors = network.get_neighbors(agent.id)
            for n_id in neighbors:
                neighbor_agent = agents[n_id]
                if not neighbor_agent.is_cooperator:
                    # Cooperator pays cost to punish defector
                    agent.payoff -= config.peer_punish_cost
                    neighbor_agent.payoff -= config.peer_punish_fine
                    total_costs += config.peer_punish_cost
                    total_fines += config.peer_punish_fine
                    sanctions_count += 1

        return {
            "sanction_events": float(sanctions_count),
            "total_fines": total_fines,
            "total_monitoring_cost": total_costs,
            "rewire_events": 0.0,
        }


class CentralizedPool(BaseInstitution):
    """Top-down institutional governance with tax-funded formal monitoring and fixed fines."""

    def apply_governance(
        self,
        agents: List[Agent],
        network: SocialNetwork,
        config: GovernanceConfig,
        rng: np.random.Generator,
    ) -> Dict[str, float]:
        n = len(agents)
        if n == 0:
            return {"sanction_events": 0.0, "total_fines": 0.0, "total_monitoring_cost": 0.0, "rewire_events": 0.0}

        # Deduct universal tax to fund institutional inspectorate
        for agent in agents:
            agent.payoff -= config.central_tax

        total_budget = n * config.central_tax
        # Detection probability is proportional to budget efficiency
        detection_prob = min(1.0, config.central_audit_efficiency * (total_budget / (n * max(1e-5, config.central_tax))))

        sanctions_count = 0
        total_fines = 0.0

        for agent in agents:
            if not agent.is_cooperator:
                if rng.random() < detection_prob:
                    agent.payoff -= config.central_fine
                    total_fines += config.central_fine
                    sanctions_count += 1

        return {
            "sanction_events": float(sanctions_count),
            "total_fines": total_fines,
            "total_monitoring_cost": total_budget,
            "rewire_events": 0.0,
        }


class PolycentricGovernance(BaseInstitution):
    """Ostrom-style polycentric nested governance with local monitoring, graduated sanctions,
    and dynamic social ostracism (network rewiring)."""

    def apply_governance(
        self,
        agents: List[Agent],
        network: SocialNetwork,
        config: GovernanceConfig,
        rng: np.random.Generator,
    ) -> Dict[str, float]:
        sanctions_count = 0
        total_fines = 0.0
        total_costs = 0.0
        rewire_count = 0

        cooperator_ids = [a.id for a in agents if a.is_cooperator]

        # 1. Local community monitoring and graduated sanctions
        for agent in agents:
            if agent.is_cooperator:
                # Cooperators naturally rehabilitate over time if they maintain cooperation
                if agent.offense_count > 0:
                    agent.offense_count = max(0, agent.offense_count - 1)
                continue

            # Defector inspected by neighbors in their community / social circle
            neighbors = network.get_neighbors(agent.id)
            community_coop_neighbors = [
                n_id for n_id in neighbors
                if agents[n_id].is_cooperator and agents[n_id].community_id == agent.community_id
            ]

            if community_coop_neighbors:
                # Local monitor detects over-harvest
                monitor_id = int(rng.choice(community_coop_neighbors))
                agents[monitor_id].payoff -= config.polycentric_local_cost
                total_costs += config.polycentric_local_cost

                # Graduated sanction calculation
                agent.offense_count += 1
                factor = config.polycentric_graduated_factor ** min(5, agent.offense_count - 1)
                effective_fine = config.polycentric_local_fine * factor

                agent.payoff -= effective_fine
                total_fines += effective_fine
                sanctions_count += 1

                # 2. Dynamic ostracism / rewiring:
                # Cooperators disconnect from chronic defectors and link to cooperative peers
                for coop_n_id in community_coop_neighbors:
                    rewired = network.rewire_ostracism(
                        agent_id=coop_n_id,
                        target_defector_id=agent.id,
                        cooperator_ids=cooperator_ids,
                        rewire_prob=config.polycentric_rewire_rate,
                    )
                    if rewired:
                        rewire_count += 1

        return {
            "sanction_events": float(sanctions_count),
            "total_fines": total_fines,
            "total_monitoring_cost": total_costs,
            "rewire_events": float(rewire_count),
        }


def create_institution(regime_name: str) -> BaseInstitution:
    """Factory function for instantiating governance regimes."""
    mapping = {
        "open_access": OpenAccess,
        "peer_punishment": PeerPunishment,
        "centralized_pool": CentralizedPool,
        "polycentric": PolycentricGovernance,
    }
    regime = regime_name.lower()
    if regime not in mapping:
        raise ValueError(f"Unknown governance regime: {regime_name}. Supported: {list(mapping.keys())}")
    return mapping[regime]()
