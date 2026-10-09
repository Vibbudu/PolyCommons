"""Configuration dataclasses for the PolyCommons simulation framework."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EcologyConfig:
    """Parameters governing common-pool resource growth and ecological tipping dynamics."""
    carrying_capacity: float = 2000.0
    regeneration_rate: float = 0.25
    tipping_threshold: float = 350.0  # Critical threshold R_crit (Allee collapse below this)
    tipping_steepness: float = 0.03
    stochastic_shock_std: float = 0.0
    initial_stock: float = 1600.0
    min_stock: float = 0.0


@dataclass
class AgentConfig:
    """Parameters governing harvesting agents, payoffs, and evolutionary learning."""
    n_agents: int = 100
    harvest_sustainable: float = 0.6   # Cooperative harvest effort (< MSY per capita)
    harvest_over: float = 2.0          # Defecting / over-harvest effort (> MSY per capita)
    extraction_cost_unit: float = 0.2  # Cost per unit effort
    resource_market_price: float = 2.0 # Value per unit of extracted stock
    selection_intensity: float = 1.5   # Beta in Fermi strategy update
    mutation_rate: float = 0.01        # Exploration / innovation rate
    initial_coop_fraction: float = 0.4 # Starts with minority cooperators to test emergence


@dataclass
class NetworkConfig:
    """Parameters for social contact topology and institutional clustering."""
    topology: str = "stochastic_block"  # 'small_world', 'scale_free', 'stochastic_block', 'random_regular'
    k_neighbors: int = 6                # Average degree or lattice neighborhood
    rewire_prob: float = 0.1            # Watts-Strogatz rewiring parameter
    m_attach: int = 3                   # Barabasi-Albert attachment count
    n_communities: int = 4              # Polycentric jurisdictions / SBM blocks
    p_in: float = 0.25                  # Intra-community edge probability
    p_out: float = 0.02                 # Inter-community edge probability


@dataclass
class GovernanceConfig:
    """Parameters specifying institutional rules, monitoring, sanctions, and dynamic rewiring."""
    regime: str = "polycentric"         # 'open_access', 'peer_punishment', 'centralized_pool', 'polycentric'
    peer_punish_cost: float = 0.25      # Cost to punisher in peer punishment
    peer_punish_fine: float = 0.9       # Penalty imposed on over-harvester
    central_tax: float = 0.15           # Fixed tax per agent for pool punishment
    central_audit_efficiency: float = 0.75  # Detection probability per audit budget
    central_fine: float = 1.8           # Top-down institutional fine
    polycentric_rewire_rate: float = 0.12   # Probability of ostracizing/rewiring away from defectors
    polycentric_graduated_factor: float = 1.4 # Graduated sanction multiplier for repeat offenders
    polycentric_local_fine: float = 1.1
    polycentric_local_cost: float = 0.1


@dataclass
class SimulationConfig:
    """Full simulation configuration container."""
    n_steps: int = 200
    seed: Optional[int] = 42
    ecology: EcologyConfig = field(default_factory=EcologyConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
