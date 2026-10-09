# PolyCommons

Agent-based model of coupled socio-ecological common-pool resource dilemmas on complex networks.

PolyCommons investigates how evolutionary game dynamics, resource replenishment, and institutional governance interact. The simulation models agents harvesting from shared ecological stocks with non-linear logistic replenishment and critical tipping points (Allee effects). It compares four institutional regimes: unregulated open access, decentralized peer sanctions, centralized pool punishment, and polycentric modular governance with dynamic network rewiring.

Targeted toward computational ecology and evolutionary game theory frameworks in complexity science (such as the Complexity Science and Evolution Unit at OIST).

## Key Features

- Coupled Socio-Ecological Dynamics: Logistic growth substrate coupled with biomass tipping thresholds and stock-dependent catch efficiency.
- Dynamic Network Topologies: Stochastic Block Models (polycentric communities), Watts-Strogatz small-world, Barabasi-Albert scale-free, and dynamic ostracism rewiring.
- Four Governance Regimes:
  1. Open Access (Hardin's tragedy of the commons baseline)
  2. Peer Punishment (decentralized costly sanctions among neighbors)
  3. Centralized Pool Punishment (tax-funded monitoring and formal fines)
  4. Polycentric Governance (nested community monitoring, graduated sanctions, and dynamic rewiring)
- Evolutionary Strategy Updating: Pairwise comparison Fermi imitation rule with selection intensity beta and exploratory mutation.
- Experiment Suite: Automated parameter sweeps, 2D phase diagrams, resilience shock testing, and network visualization.

## Project Structure

```
polycommons/
  __init__.py         Package exports
  config.py           Dataclasses for ecology, agent, network, and governance parameters
  ecology.py          Resource stock dynamics, Allee tipping functions, and harvest rationing
  network.py          Complex network builders, community partitions, and ostracism rewiring
  agents.py           Agent state, harvest effort, payoffs, and Fermi rule updating
  institutions.py     Governance interfaces and regime implementations
  engine.py           Simulation orchestrator and step loop
  analytics.py        Cooperation rate, Gini coefficient, and network metrics
  visualization.py    Plotting routines for regime comparisons, phase diagrams, and graph layouts
experiments/
  run_regime_comparison.py       Comparative trajectories across 4 governance regimes
  run_phase_diagram.py           Parameter sweep over rewiring rate vs temptation
  run_tipping_resilience.py      Acute resource shock and recovery experiment
  run_network_topology_snapshot.py Graph visualization of cooperator clusters and defectors
tests/
  test_ecology.py                Ecological growth, rationing, and tipping point tests
  test_institutions.py           Sanction, tax, and graduated fine tests
  test_network.py                Graph generation and rewiring tests
  test_engine.py                 Simulation loop and shock tests
docs/
  RESEARCH_REPORT.md             Full academic paper and mathematical specification
outputs/                         Generated figures and experiment data
```

## Installation

Requires Python 3.10 or later.

```bash
git clone https://github.com/Vibbudu/PolyCommons.git
cd PolyCommons

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Running Tests

Run the test suite using pytest:

```bash
pytest tests -v
```

All 11 unit tests verify conservation laws, payoff algebra, Fermi transition probabilities, and network rewiring integrity.

## Running Experiments

Run the comparative evaluation:
```bash
python experiments/run_regime_comparison.py
```
Outputs trajectory plots comparing resource stock, cooperation rate, Gini inequality, and sanctions over time to `outputs/regime_comparison_trajectories.png`.

Run the 2D phase diagram sweep:
```bash
python experiments/run_phase_diagram.py
```
Sweeps rewiring flexibility against over-harvest temptation, saving the cooperation survival contour to `outputs/phase_diagram_rewire_vs_temptation.png`.

Run the tipping resilience experiment:
```bash
python experiments/run_tipping_resilience.py
```
Introduces an acute resource depletion shock near the Allee threshold, saving results to `outputs/ecological_tipping_hysteresis.png`.

Generate the network topology snapshot:
```bash
python experiments/run_network_topology_snapshot.py
```
Saves the agent interaction graph visualization to `outputs/network_governance_snapshot.png`.

## Model Formulation Summary

1. Resource Dynamics:
   R_{t+1} = max(0, R_t + r * R_t * (1 - R_t / K) * Phi(R_t; R_crit, s) - H_{total,t} + noise)
   where Phi is a sigmoid scaling factor representing Allee collapse below R_crit.

2. Agent Payoff:
   pi_i = price * y_i - cost * e_i - taxes - sanctions

3. Fermi Imitation Probability:
   W(s_i <- s_j) = 1 / (1 + exp(-beta * (pi_j - pi_i)))

For full mathematical derivations, model assumptions, and analysis, see `docs/RESEARCH_REPORT.md`.

## License

MIT License.
