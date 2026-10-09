"""Computes a 2D phase diagram of cooperation survival across rewiring flexibility and over-harvest temptation."""

from pathlib import Path
import numpy as np

from polycommons.config import (
    SimulationConfig,
    EcologyConfig,
    AgentConfig,
    NetworkConfig,
    GovernanceConfig,
)
from polycommons.engine import PolyCommonsSim
from polycommons.visualization import plot_phase_diagram


def run_phase_sweep():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    n_x = 10
    n_y = 10
    rewire_rates = np.linspace(0.0, 0.30, n_x)
    temptations = np.linspace(0.8, 2.6, n_y)

    coop_grid = np.zeros((n_y, n_x))
    n_seeds = 3

    print(f"Executing phase diagram sweep ({n_y}x{n_x} grid, {n_seeds} seeds per point)...")

    for i, e_over in enumerate(temptations):
        for j, omega in enumerate(rewire_rates):
            seed_coops = []
            for seed in [101, 202, 303]:
                cfg = SimulationConfig(
                    n_steps=100,
                    seed=seed,
                    ecology=EcologyConfig(
                        carrying_capacity=2000.0,
                        regeneration_rate=0.25,
                        tipping_threshold=350.0,
                        initial_stock=1500.0,
                    ),
                    agents=AgentConfig(
                        n_agents=80,
                        harvest_sustainable=0.6,
                        harvest_over=float(e_over),
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
                        regime="polycentric",
                        polycentric_rewire_rate=float(omega),
                        polycentric_local_fine=1.5,
                        polycentric_graduated_factor=1.4,
                        polycentric_local_cost=0.06,
                    ),
                )
                sim = PolyCommonsSim(cfg)
                df = sim.run()
                seed_coops.append(df["cooperation_rate"].iloc[-20:].mean())

            coop_grid[i, j] = np.mean(seed_coops)
        print(f"  Row {i+1}/{n_y} complete (Temptation e_over = {e_over:.2f})")

    np.save(out_dir / "phase_diagram_matrix.npy", coop_grid)

    plot_path = out_dir / "phase_diagram_rewire_vs_temptation.png"
    plot_phase_diagram(
        x_vals=rewire_rates,
        y_vals=temptations,
        matrix=coop_grid,
        x_label="Polycentric Ostracism / Rewiring Rate (omega)",
        y_label="Defector Over-Harvest Temptation (e_over)",
        title="Phase Diagram: Cooperation Survival Frontier under Polycentric Governance",
        colorbar_label="Mean Stationary Cooperation Fraction",
        save_path=str(plot_path),
    )
    print(f"Phase diagram figure saved to {plot_path}")


if __name__ == "__main__":
    run_phase_sweep()
