"""Runs a comparative experiment across the four institutional governance regimes."""

from pathlib import Path
import pandas as pd

from polycommons.config import (
    SimulationConfig,
    EcologyConfig,
    AgentConfig,
    NetworkConfig,
    GovernanceConfig,
)
from polycommons.engine import PolyCommonsSim
from polycommons.visualization import plot_regime_comparison


def run_regimes():
    regimes = ["open_access", "peer_punishment", "centralized_pool", "polycentric"]
    results = {}
    summary_rows = []

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Running 4-regime comparative evaluation (200 time steps)...")

    for reg in regimes:
        cfg = SimulationConfig(
            n_steps=200,
            seed=42,
            ecology=EcologyConfig(
                carrying_capacity=2000.0,
                regeneration_rate=0.25,
                tipping_threshold=350.0,
                initial_stock=1500.0,
            ),
            agents=AgentConfig(
                n_agents=100,
                harvest_sustainable=0.6,
                harvest_over=2.0,
                selection_intensity=1.5,
                mutation_rate=0.01,
                initial_coop_fraction=0.4,
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
        df = sim.run()
        results[reg] = df

        final_stock = df["resource_stock"].iloc[-1]
        final_coop = df["cooperation_rate"].iloc[-1]
        final_gini = df["gini_wealth"].iloc[-1]
        total_sanctions = df["sanction_events"].sum()

        summary_rows.append({
            "regime": reg,
            "final_resource_stock": final_stock,
            "final_cooperation_rate": final_coop,
            "final_gini_wealth": final_gini,
            "total_sanctions": total_sanctions,
        })
        print(f"  [{reg}] Final Stock: {final_stock:.1f}, Final Coop: {final_coop:.2f}, Gini: {final_gini:.3f}")

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(out_dir / "regime_comparison_summary.csv", index=False)

    plot_path = out_dir / "regime_comparison_trajectories.png"
    plot_regime_comparison(
        dfs=results,
        carrying_capacity=2000.0,
        tipping_threshold=350.0,
        save_path=str(plot_path),
    )
    print(f"Figure saved to {plot_path}")


if __name__ == "__main__":
    run_regimes()
