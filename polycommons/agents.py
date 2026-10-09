"""Agent state representation, harvest behavior, payoffs, and evolutionary learning."""

from typing import List, Optional
import numpy as np
from polycommons.config import AgentConfig


class Agent:
    """An individual harvesting agent within the socio-ecological dilemma."""

    def __init__(self, agent_id: int, is_cooperator: bool, community_id: int = 0):
        self.id = agent_id
        self.is_cooperator = is_cooperator
        self.community_id = community_id
        self.payoff: float = 0.0
        self.wealth: float = 0.0
        self.offense_count: int = 0  # History of infractions for graduated sanctions

    def get_requested_harvest(self, config: AgentConfig) -> float:
        """Determines harvest effort depending on cooperation strategy."""
        return config.harvest_sustainable if self.is_cooperator else config.harvest_over

    def compute_base_payoff(self, realized_harvest: float, config: AgentConfig) -> float:
        """Calculates market revenue minus extraction cost."""
        effort = self.get_requested_harvest(config)
        revenue = realized_harvest * config.resource_market_price
        cost = effort * config.extraction_cost_unit
        return revenue - cost

    def update_strategy_fermi(
        self,
        neighbor_payoffs: List[float],
        neighbor_strategies: List[bool],
        config: AgentConfig,
        rng: np.random.Generator,
    ) -> None:
        """Updates strategy using pairwise comparison Fermi rule and mutation."""
        # Mutation / innovation exploration
        if rng.random() < config.mutation_rate:
            self.is_cooperator = bool(rng.random() < 0.5)
            return

        if not neighbor_payoffs:
            return

        # Choose a random role model among neighbors
        idx = int(rng.integers(0, len(neighbor_payoffs)))
        role_model_payoff = neighbor_payoffs[idx]
        role_model_strategy = neighbor_strategies[idx]

        if role_model_strategy == self.is_cooperator:
            return

        # Fermi imitation probability
        payoff_diff = role_model_payoff - self.payoff
        beta = max(1e-6, config.selection_intensity)
        # Numerical guard against overflow
        exp_arg = -beta * payoff_diff
        exp_arg = float(np.clip(exp_arg, -50.0, 50.0))
        prob_switch = 1.0 / (1.0 + np.exp(exp_arg))

        if rng.random() < prob_switch:
            self.is_cooperator = role_model_strategy
