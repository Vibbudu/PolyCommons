"""Tests socio-ecological resilience and tipping point avoidance under an acute resource depletion shock."""

from pathlib import Path
from polycommons.config import (
    SimulationConfig,
    EcologyConfig,
    AgentConfig,
    NetworkConfig,
    GovernanceConfig,
)
from polycommons.engine import PolyCommonsSim
from polycommons.visualization import plot_tipping_resilience


def run_resilience_test():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    regimes = ["open_access", "peer_punishment", "centralized_pool", "polycentric"]
    results = {}

    shock_step = 50
    shock_magnitude = 450.0  # Pushes resource close to critical threshold

    print(f"Running ecological resilience and shock recovery experiment (shock at step {shock_step})...")

    for reg in regimes:
        cfg = SimulationConfig(
            n_steps=150,
            seed=42,
            ecology=EcologyConfig(
                carrying_capacity=2000.0,
                regeneration_rate=0.25,
                tipping_threshold=350.0,
                tipping_steepness=0.03,
                initial_stock=1500.0,
            ),
            agents=AgentConfig(
                n_agents=100,
                harvest_sustainable=0.6,
                harvest_over=2.0,
                selection_intensity=1.5,
                mutation_rate=0.01,
                initial_coop_fraction=0.6,
            ),
            network=NetworkConfig(
                topology="stochastic_block",
                n_communities=4,
                p_in=0.25,
                p_out=0.02,
            ),
            governance=GovernanceConfig(
                regime=reg,
                peer_punish_cost=0.35,
                peer_punish_fine=1.6,
                central_tax=0.25,
                central_audit_efficiency=0.85,
                central_fine=3.0,
                polycentric_rewire_rate=0.18,
                polycentric_local_fine=1.5,
                polycentric_graduated_factor=1.4,
                polycentric_local_cost=0.06,
            ),
        )

        sim = PolyCommonsSim(cfg)
        df = sim.run_with_shock(shock_step=shock_step, shock_magnitude=shock_magnitude)
        results[reg] = df

        post_stock = df["resource_stock"].iloc[-1]
        post_coop = df["cooperation_rate"].iloc[-1]
        print(f"  [{reg}] Post-Shock Final Stock: {post_stock:.1f}, Cooperation: {post_coop:.2f}")

    plot_path = out_dir / "ecological_tipping_hysteresis.png"
    plot_tipping_resilience(
        dfs=results,
        shock_step=shock_step,
        tipping_threshold=350.0,
        save_path=str(plot_path),
    )
    print(f"Resilience figure saved to {plot_path}")


if __name__ == "__main__":
    run_resilience_test()
