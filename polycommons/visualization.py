"""Publication-grade visualization suite for coupled socio-ecological dilemma dynamics."""

from pathlib import Path
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


def set_academic_style() -> None:
    """Configures clean scientific typography and styling for figures."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.titlesize": 13,
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
        "grid.color": "#e0e0e0",
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
    })


REGIME_COLORS = {
    "open_access": "#c0392b",         # Crimson
    "peer_punishment": "#e67e22",     # Ochre / Amber
    "centralized_pool": "#2980b9",    # Steel Blue
    "polycentric": "#27ae60",         # Forest Green
}

REGIME_LABELS = {
    "open_access": "Open Access (Tragedy of Commons)",
    "peer_punishment": "Decentralized Peer Punishment",
    "centralized_pool": "Centralized Pool Punishment",
    "polycentric": "Polycentric Governance (Ostrom)",
}


def plot_regime_comparison(
    dfs: Dict[str, pd.DataFrame],
    carrying_capacity: float = 1000.0,
    tipping_threshold: float = 200.0,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Creates a 4-panel comparative figure of the 4 institutional governance regimes."""
    set_academic_style()
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), dpi=300)

    # Panel A: Ecological Resource Stock
    ax_res = axes[0, 0]
    for regime_key, df in dfs.items():
        color = REGIME_COLORS.get(regime_key, "#555555")
        label = REGIME_LABELS.get(regime_key, regime_key)
        ax_res.plot(df.index, df["resource_stock"], color=color, label=label, linewidth=2.0)

    ax_res.axhline(carrying_capacity, color="#7f8c8d", linestyle=":", linewidth=1.2, label="Carrying Capacity (K)")
    ax_res.axhline(tipping_threshold, color="#c0392b", linestyle="--", linewidth=1.2, label="Tipping Threshold (R_crit)")
    ax_res.set_ylabel("Resource Stock R(t)")
    ax_res.set_title("(a) Common-Pool Resource Stock Trajectory", loc="left", fontweight="bold")
    ax_res.set_ylim(bottom=0)
    ax_res.legend(frameon=True, facecolor="white", framealpha=0.9, loc="lower left")

    # Panel B: Proportion of Cooperators
    ax_coop = axes[0, 1]
    for regime_key, df in dfs.items():
        color = REGIME_COLORS.get(regime_key, "#555555")
        label = REGIME_LABELS.get(regime_key, regime_key)
        ax_coop.plot(df.index, df["cooperation_rate"], color=color, label=label, linewidth=2.0)

    ax_coop.set_ylabel("Cooperation Fraction f_C(t)")
    ax_coop.set_title("(b) Evolution of Cooperation over Time", loc="left", fontweight="bold")
    ax_coop.set_ylim(-0.02, 1.02)
    ax_coop.legend(frameon=True, facecolor="white", framealpha=0.9, loc="center left")

    # Panel C: Wealth Gini Inequality
    ax_gini = axes[1, 0]
    for regime_key, df in dfs.items():
        color = REGIME_COLORS.get(regime_key, "#555555")
        label = REGIME_LABELS.get(regime_key, regime_key)
        ax_gini.plot(df.index, df["gini_wealth"], color=color, label=label, linewidth=1.8)

    ax_gini.set_xlabel("Simulation Step (t)")
    ax_gini.set_ylabel("Wealth Gini Coefficient")
    ax_gini.set_title("(c) Economic Inequality Dynamics", loc="left", fontweight="bold")
    ax_gini.set_ylim(-0.02, 1.02)

    # Panel D: Institutional Activity / Sanctions Count
    ax_sanc = axes[1, 1]
    for regime_key, df in dfs.items():
        color = REGIME_COLORS.get(regime_key, "#555555")
        label = REGIME_LABELS.get(regime_key, regime_key)
        # Compute rolling window of sanction events for smooth visualization
        sanc_smooth = df["sanction_events"].rolling(window=5, min_periods=1).mean()
        ax_sanc.plot(df.index, sanc_smooth, color=color, label=label, linewidth=1.8)

    ax_sanc.set_xlabel("Simulation Step (t)")
    ax_sanc.set_ylabel("Sanction Events (5-step MA)")
    ax_sanc.set_title("(d) Enforcement & Monitoring Pressure", loc="left", fontweight="bold")

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_phase_diagram(
    x_vals: np.ndarray,
    y_vals: np.ndarray,
    matrix: np.ndarray,
    x_label: str,
    y_label: str,
    title: str,
    colorbar_label: str = "Final Cooperation Fraction",
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Generates a 2D contour heatmap phase diagram showing cooperation survival frontiers."""
    set_academic_style()
    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)

    x_mesh, y_mesh = np.meshgrid(x_vals, y_vals)
    cmap = plt.cm.viridis

    contour = ax.contourf(x_mesh, y_mesh, matrix, levels=20, cmap=cmap, vmin=0.0, vmax=1.0)
    cbar = fig.colorbar(contour, ax=ax, shrink=0.85)
    cbar.set_label(colorbar_label, fontsize=10)

    # Add contour line for the 50% cooperation threshold
    ax.contour(x_mesh, y_mesh, matrix, levels=[0.5], colors=["#ffffff"], linewidths=[2.0], linestyles=["--"])

    ax.set_xlabel(x_label, fontsize=11)
    ax.set_ylabel(y_label, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_tipping_resilience(
    dfs: Dict[str, pd.DataFrame],
    shock_step: int,
    tipping_threshold: float = 200.0,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Generates resilience trajectories following an acute ecological shock."""
    set_academic_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

    for regime_key, df in dfs.items():
        color = REGIME_COLORS.get(regime_key, "#555555")
        label = REGIME_LABELS.get(regime_key, regime_key)
        ax1.plot(df.index, df["resource_stock"], color=color, label=label, linewidth=2.0)
        ax2.plot(df.index, df["cooperation_rate"], color=color, label=label, linewidth=2.0)

    for ax in (ax1, ax2):
        ax.axvline(shock_step, color="#8e44ad", linestyle=":", linewidth=1.5, label="Ecological Shock")

    ax1.axhline(tipping_threshold, color="#c0392b", linestyle="--", linewidth=1.2, label="Tipping Threshold (R_crit)")
    ax1.set_xlabel("Simulation Step (t)")
    ax1.set_ylabel("Resource Stock R(t)")
    ax1.set_title("(a) Post-Shock Resource Trajectory & Regime Shifts", loc="left", fontweight="bold")
    ax1.set_ylim(bottom=0)
    ax1.legend(frameon=True, facecolor="white", framealpha=0.9, loc="best")

    ax2.set_xlabel("Simulation Step (t)")
    ax2.set_ylabel("Cooperation Fraction f_C(t)")
    ax2.set_title("(b) Behavioral Response & Norm Resilience", loc="left", fontweight="bold")
    ax2.set_ylim(-0.02, 1.02)
    ax2.legend(frameon=True, facecolor="white", framealpha=0.9, loc="best")

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def plot_network_governance_snapshot(
    sim,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Visualizes social network structure with node strategies and community boundaries."""
    set_academic_style()
    fig, ax = plt.subplots(figsize=(9, 8), dpi=300)

    g = sim.network.graph
    pos = nx.spring_layout(g, seed=sim.config.seed, k=0.25)

    coop_nodes = [a.id for a in sim.agents if a.is_cooperator]
    defect_nodes = [a.id for a in sim.agents if not a.is_cooperator]

    # Draw edges
    nx.draw_networkx_edges(g, pos, ax=ax, alpha=0.25, edge_color="#7f8c8d", width=0.8)

    # Draw cooperators
    if coop_nodes:
        nx.draw_networkx_nodes(
            g, pos, nodelist=coop_nodes, ax=ax,
            node_color="#27ae60", node_size=60, alpha=0.9, label="Cooperator (Sustainable)"
        )

    # Draw defectors
    if defect_nodes:
        nx.draw_networkx_nodes(
            g, pos, nodelist=defect_nodes, ax=ax,
            node_color="#c0392b", node_size=60, alpha=0.9, label="Defector (Over-harvester)"
        )

    ax.set_title("Network Topology and Behavioral Clustering (Polycentric Regime)", fontsize=12, fontweight="bold")
    ax.axis("off")
    ax.legend(frameon=True, facecolor="white", framealpha=0.9, loc="upper right")

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig
