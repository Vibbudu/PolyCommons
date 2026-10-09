"""Core discrete-time agent-based simulation loop orchestrating agents, ecology, and institutions."""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from polycommons.agents import Agent
from polycommons.analytics import compute_step_summary
from polycommons.config import SimulationConfig
from polycommons.ecology import ResourceStock
from polycommons.institutions import BaseInstitution, create_institution
from polycommons.network import SocialNetwork


class PolyCommonsSim:
    """Simulation engine for coupled socio-ecological network dynamics."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        
        # Ecological substrate
        self.resource = ResourceStock(config.ecology, seed=config.seed)
        
        # Social interaction network
        self.network = SocialNetwork(
            n_agents=config.agents.n_agents,
            config=config.network,
            seed=config.seed,
        )
        
        # Governance institution
        self.institution: BaseInstitution = create_institution(config.governance.regime)
        
        # Initialize population
        self.agents: List[Agent] = []
        self._init_agents()
        
        # Logged metrics history
        self.history: List[Dict[str, float]] = []

    def _init_agents(self) -> None:
        """Instantiates agents with configured strategy distribution and community assignments."""
        n = self.config.agents.n_agents
        p_coop = self.config.agents.initial_coop_fraction
        
        # Random initial strategy assignment
        is_coop_flags = self.rng.random(n) < p_coop
        
        self.agents = [
            Agent(
                agent_id=i,
                is_cooperator=bool(is_coop_flags[i]),
                community_id=self.network.get_community(i),
            )
            for i in range(n)
        ]

    def step(self, external_shock: float = 0.0) -> Dict[str, float]:
        """Advances the coupled system by one time step."""
        # Apply external shock to resource if specified
        if external_shock > 0:
            self.resource.stock = max(
                self.config.ecology.min_stock,
                self.resource.stock - external_shock,
            )

        # 1. Harvest extraction phase
        requested = np.array([a.get_requested_harvest(self.config.agents) for a in self.agents])
        realized = self.resource.harvest_and_step(requested)

        # 2. Base market payoff calculation
        for i, agent in enumerate(self.agents):
            agent.payoff = agent.compute_base_payoff(realized[i], self.config.agents)

        # 3. Governance institution audits, taxes, sanctions, and dynamic rewiring
        gov_metrics = self.institution.apply_governance(
            self.agents, self.network, self.config.governance, self.rng
        )

        # 4. Wealth accumulation
        for agent in self.agents:
            agent.wealth += agent.payoff

        # 5. Evolutionary strategy update (Fermi pairwise comparison)
        current_payoffs = [a.payoff for a in self.agents]
        current_strategies = [a.is_cooperator for a in self.agents]

        for agent in self.agents:
            neighbors = self.network.get_neighbors(agent.id)
            if not neighbors:
                continue

            n_payoffs = [current_payoffs[n_id] for n_id in neighbors]
            n_strats = [current_strategies[n_id] for n_id in neighbors]

            agent.update_strategy_fermi(
                neighbor_payoffs=n_payoffs,
                neighbor_strategies=n_strats,
                config=self.config.agents,
                rng=self.rng,
            )

        # 6. Compute and record summary metrics
        metrics = compute_step_summary(
            agents=self.agents,
            network=self.network,
            resource_stock=self.resource.stock,
            carrying_capacity=self.config.ecology.carrying_capacity,
            governance_metrics=gov_metrics,
        )
        self.history.append(metrics)
        return metrics

    def run(self, n_steps: Optional[int] = None) -> pd.DataFrame:
        """Executes simulation for specified number of steps and returns history DataFrame."""
        total_steps = n_steps if n_steps is not None else self.config.n_steps
        for _ in range(total_steps):
            self.step()

        df = pd.DataFrame(self.history)
        df.index.name = "step"
        return df

    def run_with_shock(
        self,
        shock_step: int,
        shock_magnitude: float,
        n_steps: Optional[int] = None,
    ) -> pd.DataFrame:
        """Executes simulation and introduces an acute resource depletion shock at shock_step."""
        total_steps = n_steps if n_steps is not None else self.config.n_steps
        for t in range(total_steps):
            shock = shock_magnitude if t == shock_step else 0.0
            self.step(external_shock=shock)

        df = pd.DataFrame(self.history)
        df.index.name = "step"
        return df

    def reset(self) -> None:
        """Resets the simulation to initial conditions."""
        self.rng = np.random.default_rng(self.config.seed)
        self.resource.reset()
        self.network = SocialNetwork(
            n_agents=self.config.agents.n_agents,
            config=self.config.network,
            seed=self.config.seed,
        )
        self.institution = create_institution(self.config.governance.regime)
        self.history = []
        self._init_agents()
