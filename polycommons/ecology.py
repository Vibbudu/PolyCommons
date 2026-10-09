"""Ecological resource dynamics with non-linear growth and tipping point thresholds."""

from typing import List, Optional
import numpy as np
from polycommons.config import EcologyConfig


class ResourceStock:
    """Represents a common-pool resource with logistic growth and Allee tipping effects.
    
    The discrete-time dynamics:
      R_{t+1} = max(0, R_t + delta_R(R_t) - Harvest_t + shock)
    where:
      delta_R(R) = r * R * (1 - R / K) * TippingFactor(R)
      TippingFactor(R) = 1 / (1 + exp(-s * (R - R_crit)))
    """

    def __init__(self, config: EcologyConfig, seed: Optional[int] = None):
        self.config = config
        self.rng = np.random.default_rng(seed)
        self.stock: float = float(config.initial_stock)
        self.history: List[float] = [self.stock]
        self.harvest_history: List[float] = []

    def tipping_factor(self, stock: float) -> float:
        """Sigmoidal scaling factor representing Allee effect / tipping threshold."""
        if self.config.tipping_steepness <= 0:
            return 1.0 if stock >= self.config.tipping_threshold else 0.0
        val = self.config.tipping_steepness * (stock - self.config.tipping_threshold)
        # Prevent floating overflow
        val = np.clip(val, -50.0, 50.0)
        return float(1.0 / (1.0 + np.exp(-val)))

    def ecological_regeneration(self, stock: float) -> float:
        """Logistic growth modulated by the critical tipping threshold."""
        if stock <= self.config.min_stock:
            return 0.0
        growth = (
            self.config.regeneration_rate
            * stock
            * (1.0 - (stock / self.config.carrying_capacity))
            * self.tipping_factor(stock)
        )
        return max(0.0, float(growth))

    def abundance_factor(self) -> float:
        """Catch-per-unit-effort efficiency factor based on current stock abundance.
        
        When stock is severely depleted, extracting resources becomes harder and yields drop.
        """
        ref_level = 0.5 * self.config.carrying_capacity
        if ref_level <= 0:
            return 1.0
        return float(np.clip(self.stock / ref_level, 0.05, 1.0))

    def harvest_and_step(self, requested_harvests: np.ndarray) -> np.ndarray:
        """Processes extraction requests and advances ecological state by one time step.
        
        Args:
            requested_harvests: 1D array of harvest efforts by all agents.
            
        Returns:
            realized_harvests: 1D array of actual harvest obtained by each agent.
        """
        total_requested = float(np.sum(requested_harvests))
        efficiency = self.abundance_factor()
        effective_demand = total_requested * efficiency

        if effective_demand <= 0:
            realized = np.zeros_like(requested_harvests)
            total_extracted = 0.0
        elif effective_demand <= self.stock:
            # Full harvest realized with abundance efficiency
            realized = requested_harvests * efficiency
            total_extracted = effective_demand
        else:
            # Over-extraction: resource stock is depleted to zero and rationed proportionally
            ration_ratio = self.stock / effective_demand
            realized = requested_harvests * efficiency * ration_ratio
            total_extracted = self.stock

        # Add ecological growth
        growth = self.ecological_regeneration(self.stock)
        
        # Stochastic climate / environmental shock
        shock = 0.0
        if self.config.stochastic_shock_std > 0:
            shock = float(self.rng.normal(0.0, self.config.stochastic_shock_std * self.stock))

        new_stock = self.stock + growth - total_extracted + shock
        self.stock = float(np.clip(new_stock, self.config.min_stock, self.config.carrying_capacity))
        
        self.history.append(self.stock)
        self.harvest_history.append(total_extracted)

        return realized

    def reset(self, initial_stock: Optional[float] = None) -> None:
        """Resets the ecological stock to initial state."""
        if initial_stock is not None:
            self.stock = float(initial_stock)
        else:
            self.stock = float(self.config.initial_stock)
        self.history = [self.stock]
        self.harvest_history = []
