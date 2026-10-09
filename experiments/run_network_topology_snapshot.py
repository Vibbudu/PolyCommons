"""Visualizes a snapshot of the agent interaction graph and behavioral clustering."""

from pathlib import Path
from polycommons.config import (
    SimulationConfig,
    EcologyConfig,
    AgentConfig,
    NetworkConfig,
    GovernanceConfig,
)
from polycommons.engine import PolyCommonsSim
from polycommons.visualization import plot_network_governance_snapshot


def run_network_snapshot():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Generating network topology snapshot...")

    cfg = SimulationConfig(
        n_steps=60,
        seed=42,
        ecology=EcologyConfig(
            carrying_capacity=1000.0,
            regeneration_rate=0.25,
            tipping_threshold=220.0,
            initial_stock=750.0,
        ),
        agents=AgentConfig(
            n_agents=80,
            harvest_sustainable=1.0,
            harvest_over=2.2,
            selection_intensity=1.2,
            mutation_rate=0.01,
            initial_coop_fraction=0.5,
        ),
        network=NetworkConfig(
            topology="stochastic_block",
            n_communities=4,
            p_in=0.25,
            p_out=0.02,
        ),
        governance=GovernanceConfig(
            regime="polycentric",
            polycentric_rewire_rate=0.15,
            polycentric_local_fine=1.2,
            polycentric_graduated_factor=1.35,
            polycentric_local_cost=0.08,
        ),
    )

    sim = PolyCommonsSim(cfg)
    sim.run()

    plot_path = out_dir / "network_governance_snapshot.png"
    plot_network_governance_snapshot(sim, save_path=str(plot_path))
    print(f"Network snapshot saved to {plot_path}")


if __name__ == "__main__":
    run_network_snapshot()
