# Governing Agentic AI Under Deep Uncertainty — Reproducibility Code

This repository contains the reproducibility code, simulation outputs, analysis scripts, and figure-generation scripts associated with the manuscript:

**Governing Agentic AI Under Deep Uncertainty: Scenario-Based Stress Tests of Institutional Containment**

The code implements a scenario-based stochastic stress test of institutional containment across alternative topologies of executable authority.

The experiment examines how governance topology and runtime mediation condition the downstream reach and persistence of an adverse executable condition after it has emerged.

## Overview

The simulation compares four five-cell governance topologies:

| Scenario | Topology | Directed edges | Density | Origin out-degree |
|---|---|---:|---:|---:|
| S0 | Maximal-Connectivity Topology | 20 | 1.00 | 4 |
| S1 | Sparse Sequential Topology | 5 | 0.25 | 1 |
| S2 | Hub-Mediated Topology | 8 | 0.40 | 4 |
| S3 | Layered Topology | 7 | 0.35 | 2 |

Each topology is evaluated across the same 196-condition parameter grid:

```text
p   ∈ {0.001, 0.005, 0.010, 0.020}
τ ∈ {0, 1, 2, 3, 4, 5, 6}
FN  ∈ {0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30}
```

With 1,000 Monte Carlo replications per topology-condition, the full experiment contains:

```text
196 conditions per topology
× 4 topologies
× 1,000 replications
= 784,000 containment episodes
```

The simulation is a structured design experiment.

It is not calibrated to empirical frequencies of real-world agentic-AI incidents, and the reported results should not be interpreted as forecasts of incident probability.

## Repository Structure

```text
agentic-containment/
├── institutional_containment_stress_test.py
├── analyze_simulation_results.py
├── plot_topology_stress_results.py
├── plot_containment_response_surfaces.py
├── plot_bounded_leakage_gap.py
├── README.md
├── CITATION.cff
├── LICENSE
├── requirements.txt
│
├── validation/
│   └── s0_reference_196.csv
│
├── simulation_output/
│   ├── scenario_sweep_784.csv
│   ├── scenario_summary.csv
│   ├── topology_manifest.json
│   ├── s0_regression_check.csv
│   ├── S0_maximal_connectivity/
│   │   └── parameter_sweep_196.csv
│   ├── S1_sparse_sequential/
│   │   └── parameter_sweep_196.csv
│   ├── S2_hub_mediated/
│   │   └── parameter_sweep_196.csv
│   └── S3_layered/
│       └── parameter_sweep_196.csv
│
├── analysis_output/
│   ├── scenario_means.csv
│   ├── topology_by_p.csv
│   ├── topology_by_tau.csv
│   ├── topology_by_fn.csv
│   ├── contrasts_vs_S0.csv
│   ├── contrasts_vs_S0_by_p.csv
│   ├── contrasts_vs_S0_by_tau.csv
│   ├── contrasts_vs_S0_by_fn.csv
│   ├── structural_checks.csv
│   ├── endpoint_contrasts.csv
│   └── anchor_condition.csv
│
└── figures/
    ├── topology_stress_results.pdf
    ├── topology_stress_results.png
    ├── containment_envelope.pdf
    ├── containment_envelope.png
    ├── containment_envelope_clean.pdf
    ├── containment_envelope_clean.png
    ├── leakage_envelope.pdf
    ├── leakage_envelope.png
    ├── leakage_envelope_clean.pdf
    ├── leakage_envelope_clean.png
    ├── bounded_leakage_gap.pdf
    └── bounded_leakage_gap.png
```

The `analysis_output/` and `figures/` directories can be regenerated from the simulation outputs using the supplied analysis and plotting scripts.

An annotated bounded-leakage-gap figure can additionally be generated with the `--annotate` option.

## Reproducibility Design

The topology-aware implementation was developed as an extension of an earlier maximal-connectivity implementation.

Before any alternative topology is evaluated, the current code is required to reproduce the previously verified S0 maximal-connectivity output exactly across all 196 parameter conditions.

The reference output is stored in:

```text
validation/s0_reference_196.csv
```

The script performs an exact column-by-column and value-by-value regression comparison between the newly generated S0 output and this verified reference.

If the regression check fails, execution stops and S1-S3 are not run.

A successful run therefore requires:

```text
[PASS] S0 exactly matches the verified 196-condition reference sweep.
```

Only after this condition is satisfied does the script execute the three alternative governance topologies.

This regression gate preserves the numerical behavior of the original maximal-connectivity model while allowing executable-authority topology to be varied.

## Governance Topologies

### S0 — Maximal-Connectivity Topology

Every governance cell has a directed executable-authority interface to every other governance cell.

S0 therefore contains 20 directed edges and serves as the maximal-connectivity benchmark.

### S1 — Sparse Sequential Topology

The directed interfaces are:

```text
1 -> 2
2 -> 3
2 -> 4
3 -> 4
4 -> 5
```

This topology represents a sparse sequential structure with limited immediate reach from the originating cell.

The scenario uses a procurement-to-payment interpretation:

```text
Supplier Intelligence
Procurement Authorization
Vendor Master
Payment Execution
Accounting and Compliance
```

### S2 — Hub-Mediated Topology

The originating orchestration cell has bidirectional interfaces with each secondary cell:

```text
1 <-> 2
1 <-> 3
1 <-> 4
1 <-> 5
```

Secondary cells have no direct interfaces to one another.

This topology gives the originating cell the same immediate reach as S0 while restricting secondary-to-secondary propagation.

The scenario uses the following institutional domains:

```text
Agent Orchestration
Internal Data Services
Communications
External APIs and Services
Privileged Enterprise Operations
```

### S3 — Layered Topology

The directed interfaces are:

```text
1 -> 2
1 -> 3
2 -> 3
2 -> 4
3 -> 4
3 -> 5
4 -> 5
```

This topology represents a layered authority structure in which adverse execution can acquire downstream consequences through successive institutional domains.

The scenario uses the following domains:

```text
Customer Operations
Customer Data
Analytics and Decision Support
External Disclosure and Partner Transfer
Compliance and Oversight
```

## Simulation Dynamics

Each replication contains:

- five purpose-bound governance cells;
- one originating cell that begins actively compromised;
- four initially uncompromised secondary cells; and
- an observation horizon of 12 abstract simulation steps.

A compromised cell is one to which an adverse executable condition has propagated.

An actively compromised cell remains capable of affecting execution and generating further propagation opportunities until effective isolation occurs.

Propagation denotes the extension of an adverse executable condition across purpose-bound domains of delegated authority.

It does not necessarily denote malware transmission or technical intrusion.

Institutionally, propagation may correspond to autonomous tool use, exercised permissions, resource access, or consequential cross-domain action.

For susceptible target cell \(j\), the per-step propagation probability is:

```text
q_j = 1 - (1 - p)^k_j
```

where \(k_j\) is the number of actively compromised source cells with a directed executable-authority interface to target cell \(j\).

A cell newly compromised during simulation step \(t\) first becomes active at step \(t+1\).

Same-step cascading is therefore excluded.

Endogenous recovery is not modeled.

## Experimental Parameters

### Propagation pressure: `p`

`p` is the per-active-source, per-susceptible-cell, per-step propagation probability.

It is an experimental stress parameter rather than an empirically calibrated incident probability.

### Mediation delay: `τ`

`τ` is the delay between successful detection and effective isolation.

Simulation steps represent abstract model time rather than fixed intervals of clock time.

The parameter can therefore be interpreted as relative organizational intervention latency associated with escalation, review, authorization, or administrative isolation.

When `τ = 0`, a successfully detected compromised cell is isolated before its first or next propagation opportunity.

### Episode-level non-detection: `FN`

`FN` is the episode-level probability that a compromised cell remains undetected throughout the modeled containment episode.

It is not a per-step false-negative probability.

## Main Outcomes

### Cross-cell leakage

Cross-cell leakage occurs when at least one secondary governance cell is compromised by the end of the observation horizon.

### Systemic contagion

Systemic contagion occurs when at least two secondary governance cells are compromised.

This is a model-internal escalation threshold rather than an empirical, legal, or normative definition of systemic harm.

### Strategic velocity

Strategic velocity measures the percentage of secondary-cell time that remains uncompromised during the observation horizon.

It represents retained distributed operating capacity rather than computational or task-processing speed.

### Propagated Exposure (PE)

Propagated Exposure measures the number of secondary governance cells reached by the adverse executable condition.

PE captures propagation breadth.

It does not measure the normative magnitude of value missing or value slippage.

### Compromised Execution Persistence (CEP)

Compromised Execution Persistence measures cumulative active compromised cell-steps across the modeled system, including the originating cell.

CEP captures the duration and institutional extent of active compromised execution.

### Bounded-leakage gap

The bounded-leakage gap is:

```text
G = Pr(L = 1) - Pr(C = 1)
  = Pr(L = 1, C = 0)
```

where `L` denotes cross-cell leakage and `C` denotes systemic contagion.

It represents the unconditional share of episodes in which an adverse executable condition reaches at least one secondary cell but does not reach at least two secondary cells within the observation horizon.

A larger bounded-leakage gap does not by itself imply better containment and should be interpreted jointly with leakage, systemic contagion, PE, CEP, and strategic velocity.

## Environment

Create and activate a Python virtual environment, then install the dependencies listed in `requirements.txt`:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The required Python packages include NumPy, pandas, and Matplotlib.

## Running the Experiment

All commands below assume that the current working directory is the repository root.

### 1. Reproduce the simulation

Run:

```bash
python institutional_containment_stress_test.py --overwrite
```

The default configuration is:

```text
replications per condition = 1,000
seed                       = 42
observation horizon        = 12 simulation steps
S0 regression reference    = ./validation/s0_reference_196.csv
output directory           = ./simulation_output
```

The equivalent fully explicit command is:

```bash
python institutional_containment_stress_test.py \
  --replicates 1000 \
  --seed 42 \
  --horizon 12 \
  --reference ./validation/s0_reference_196.csv \
  --output-dir ./simulation_output \
  --overwrite
```

The `--overwrite` option permits generated CSV and JSON files in the existing `simulation_output` directory to be replaced in place.

The output directory itself is not deleted.

This behavior avoids directory-locking problems that may arise in synchronized or cross-platform file systems.

### 2. Reproduce the descriptive analysis

After the simulation completes successfully, run:

```bash
python analyze_simulation_results.py
```

This reads:

```text
./simulation_output/scenario_sweep_784.csv
```

and writes the descriptive analysis files to:

```text
./analysis_output/
```

The analysis includes:

- design-wide scenario means;
- topology × propagation-pressure marginals;
- topology × mediation-delay marginals;
- topology × non-detection marginals;
- matched-condition contrasts relative to S0;
- endpoint contrasts;
- the manuscript anchor condition; and
- structural checks for the S0-S2 comparison.

### 3. Reproduce the topology comparison figure

Run:

```bash
python plot_topology_stress_results.py
```

This generates:

```text
figures/topology_stress_results.pdf
figures/topology_stress_results.png
```

The four panels compare the governance topologies across propagation pressure, mediation delay, and episode-level non-detection.

### 4. Reproduce the S0 containment response surfaces

Run:

```bash
python plot_containment_response_surfaces.py
```

This reads:

```text
./simulation_output/S0_maximal_connectivity/parameter_sweep_196.csv
```

and generates annotated and clean publication versions of the systemic-contagion and cross-cell-leakage response surfaces.

The principal outputs are:

```text
figures/containment_envelope.pdf
figures/containment_envelope.png
figures/containment_envelope_clean.pdf
figures/containment_envelope_clean.png

figures/leakage_envelope.pdf
figures/leakage_envelope.png
figures/leakage_envelope_clean.pdf
figures/leakage_envelope_clean.png
```

### 5. Reproduce the bounded-leakage-gap figure

Run:

```bash
python plot_bounded_leakage_gap.py
```

This generates:

```text
figures/bounded_leakage_gap.pdf
figures/bounded_leakage_gap.png
```

To generate the version with cell-level percentage-point values, run:

```bash
python plot_bounded_leakage_gap.py --annotate
```

which additionally generates:

```text
figures/bounded_leakage_gap_annotated.pdf
figures/bounded_leakage_gap_annotated.png
```

### Complete reproduction sequence

The complete workflow is therefore:

```bash
python institutional_containment_stress_test.py --overwrite
python analyze_simulation_results.py
python plot_topology_stress_results.py
python plot_containment_response_surfaces.py
python plot_bounded_leakage_gap.py
```

Optional annotated bounded-leakage figure:

```bash
python plot_bounded_leakage_gap.py --annotate
```

## Expected Verification Output

A successful simulation run should include:

```text
[PASS] Computational verification checks.
[PASS] S0 exactly matches the verified 196-condition reference sweep.
[PASS] S0 and S2 cross-cell leakage are identical across all 196 matched conditions.
[PASS] S0-S2 matched topology ordering checks.
[PASS] S0 exact regression.
[PASS] S1 Sparse Sequential Topology.
[PASS] S2 Hub-Mediated Topology.
[PASS] S3 Layered Topology.
[PASS] 784 topology-condition rows generated.
Total containment episodes: 784,000
```

## Reference Design-Wide Results

With the default configuration, the design-wide means are:

| Scenario | Systemic contagion | Cross-cell leakage | PE | Strategic velocity | CEP | Bounded-leakage gap |
|---|---:|---:|---:|---:|---:|---:|
| S0 | 3.12% | 12.84% | 0.170 | 97.35% | 5.121 | 9.72 pp |
| S1 | 0.29% | 4.26% | 0.046 | 99.26% | 4.609 | 3.97 pp |
| S2 | 1.43% | 12.84% | 0.144 | 97.61% | 5.030 | 11.41 pp |
| S3 | 0.95% | 7.14% | 0.082 | 98.68% | 4.769 | 6.18 pp |

The S0-S2 comparison is especially informative.

Both topologies give the originating cell direct executable-authority interfaces to all four secondary cells.

Accordingly, cross-cell leakage is identical across all 196 matched parameter conditions.

S2 nevertheless restricts secondary-to-secondary connectivity, reducing downstream systemic escalation relative to S0.

## Generated Simulation Files

### `scenario_sweep_784.csv`

Combined output for all four topologies and all 196 parameter conditions per topology.

The file contains 784 topology-condition rows.

### `scenario_summary.csv`

Design-wide and anchor-condition summary statistics for S0-S3.

### `topology_manifest.json`

Machine-readable documentation of:

- experimental parameters;
- topology definitions;
- adjacency matrices;
- cell labels;
- timing assumptions;
- outcome definitions;
- interpretation boundaries; and
- excluded claims.

### `s0_regression_check.csv`

Column-level report of the exact S0 regression comparison against the verified reference output.

### Per-topology `parameter_sweep_196.csv`

Each topology directory contains its corresponding 196-condition parameter sweep.

## Generated Analysis Files

The `analysis_output/` directory contains descriptive summaries used to inspect and report the simulation results.

These include:

```text
scenario_means.csv
topology_by_p.csv
topology_by_tau.csv
topology_by_fn.csv
contrasts_vs_S0.csv
contrasts_vs_S0_by_p.csv
contrasts_vs_S0_by_tau.csv
contrasts_vs_S0_by_fn.csv
structural_checks.csv
endpoint_contrasts.csv
anchor_condition.csv
```

These files are derived from `scenario_sweep_784.csv` and do not modify the underlying stochastic simulation outputs.

## Generated Figures

The `figures/` directory contains PDF and 600-dpi PNG versions of the reproduced simulation figures.

The plotting scripts read previously generated CSV outputs and do not rerun the stochastic simulation.

This separation ensures that changes to plotting code cannot alter the underlying simulation results.

## Interpretation Boundaries

The simulation does not establish that:

- governance cells guarantee complete containment;
- localized adverse execution is benign or normatively acceptable;
- the parameter values correspond to empirical incident probabilities;
- value missing or value slippage can be assigned a common numerical magnitude;
- any topology is universally optimal;
- the synthetic scenarios represent typical enterprise architectures; or
- the proposed governance architecture is superior to all alternatives.

The experiment instead tests conditional containment after an adverse executable condition has emerged.

Its purpose is to examine how the topology of executable authority and runtime mediation jointly condition the breadth and persistence of downstream adverse execution under specified stress conditions.

## Reproducibility and Numerical Stability

The pseudorandom generator is reinitialized with seed `42` for each topology and parameter condition.

This provides a reproducible matched random-number structure across the experimental design.

The stochastic kernel preserves the draw order used in the original maximal-connectivity implementation.

The S0 exact regression gate verifies that introducing topology-aware propagation does not alter the previously verified maximal-connectivity results.

## License

The code is released under the MIT License.

See `LICENSE`.

## Citation

Citation metadata are provided in `CITATION.cff`.

The repository preserves anonymous authorship during peer review.

Author-identifying metadata can be added after the review process permits deanonymization.

## Repository

https://github.com/GovArchLab/agentic-containment
