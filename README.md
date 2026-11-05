# Governing Agentic AI Under Deep Uncertainty — Reproducibility Code

This repository contains the simulation and figure-generation code associated with the manuscript:

**Governing Agentic AI Under Deep Uncertainty: Scenario-Based Stress Tests of Institutional Containment**

The code implements the scenario-based stochastic stress tests used to examine how the topology of executable authority and runtime mediation condition the downstream containment of adverse execution across purpose-bound governance cells.

## Scope

The simulation is a structured stochastic design experiment.

It begins after an adverse executable condition has emerged and examines whether its consequences remain localized or propagate across governance-cell boundaries before detection and effective isolation interrupt further spread.

The model does **not** estimate empirical frequencies of real-world agentic-AI incidents.

The parameter values are experimental stress settings, and the reported relationships characterize behavior within the specified model and parameter space rather than calibrated real-world probabilities or causal effect estimates.

Value missing and value slippage are possible institutional sources of an adverse executable condition, but they are not modeled as stochastic inputs or assigned numerical magnitudes in the propagation model.

## Governance topologies

The experiment compares four five-cell governance topologies.

| Scenario | Topology | Directed edges | Density | Origin out-degree |
|---|---|---:|---:|---:|
| S0 | Maximal-Connectivity Topology | 20 | 1.00 | 4 |
| S1 | Sparse Sequential Topology | 5 | 0.25 | 1 |
| S2 | Hub-Mediated Topology | 8 | 0.40 | 4 |
| S3 | Layered Topology | 7 | 0.35 | 2 |

The scenarios are theory-grounded synthetic structures rather than empirical reconstructions of particular organizations.

They represent stylized patterns of executable authority, including maximal connectivity, sequential process flow, hub-mediated access, and layered dependencies.

### S0: Maximal-Connectivity Topology

Every governance cell has a directed executable-authority interface to each of the other four cells.

S0 provides the maximal-connectivity benchmark.

### S1: Sparse Sequential Topology

The directed interfaces are:

```text
1 -> 2
2 -> 3
2 -> 4
3 -> 4
4 -> 5
```

The scenario represents a sparse sequential structure with limited immediate reach from the originating cell.

### S2: Hub-Mediated Topology

The originating orchestration cell has bidirectional interfaces with each secondary domain:

```text
1 <-> 2
1 <-> 3
1 <-> 4
1 <-> 5
```

S2 gives the originating cell the same immediate reach as S0 but removes direct secondary-to-secondary interfaces.

This provides the principal structural comparison for separating initial cross-cell leakage from subsequent systemic escalation.

### S3: Layered Topology

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

S3 represents a layered structure in which adverse execution can acquire downstream consequences through successive institutional domains.

## Simulation design

Each replication contains:

- `N = 5` purpose-bound governance cells;
- an observation horizon of `H = 12` simulation steps;
- one originating cell that begins actively compromised; and
- four initially uncompromised secondary cells.

A compromised cell is one to which an adverse executable condition has propagated.

An actively compromised cell remains capable of affecting execution and serving as a source of subsequent propagation until effective isolation occurs.

Propagation represents the extension of an adverse executable condition across domains of delegated authority rather than necessarily malware transmission or technical intrusion.

Institutionally, such propagation may correspond to autonomous tool use, exercised permissions, resource access, or consequential cross-domain action.

A cell newly compromised during simulation step `t` first becomes active at step `t + 1`, so same-step cascading is excluded.

Endogenous recovery is not modeled.

## Experimental parameters

The common parameter grid is:

```text
p   ∈ {0.001, 0.005, 0.010, 0.020}
τ  ∈ {0, 1, 2, 3, 4, 5, 6}
FN  ∈ {0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30}
```

where:

- `p` is the per-active-source, per-susceptible-cell, per-step propagation probability;
- `τ` is the mediation delay between detection and effective isolation; and
- `FN` is the episode-level probability that a compromised cell remains undetected throughout the modeled containment episode.

`p` is an experimental propagation-pressure parameter rather than an empirically calibrated incident probability.

`τ` is an abstract model-time parameter rather than a fixed interval of clock time.

It represents relative intervention latency and can be interpreted in organizational terms as delay associated with escalation, review, authorization, or administrative isolation.

`FN` is an episode-level non-detection probability, not a per-step false-negative rate.

When `τ = 0`, a detected cell is isolated before its first or next propagation opportunity.

Each topology is evaluated under:

```text
4 × 7 × 7 = 196 parameter conditions
```

with:

```text
1,000 stochastic replications per condition
196,000 containment episodes per topology
784,000 containment episodes across four topologies
```

The pseudorandom generator is reinitialized with seed `42` for each parameter condition and topology.

This ensures reproducibility while supporting matched comparisons across operating conditions and governance structures.

## Main outcomes

### Cross-cell leakage

Cross-cell leakage occurs when at least one secondary governance cell has been compromised by the end of the observation horizon.

### Systemic contagion

Systemic contagion occurs when at least two secondary governance cells have been compromised.

This is a model-internal escalation threshold.

It should not be interpreted as an empirical, legal, or normative definition of systemic harm.

### Strategic velocity

Strategic velocity measures the share of secondary-cell time during which the four secondary governance cells remain uncompromised.

It represents retained distributed operating capacity rather than task speed or computational throughput.

### Propagated exposure (PE)

Propagated exposure measures the number of secondary governance cells reached by the adverse executable condition by the end of the observation horizon.

PE measures downstream propagation breadth rather than the normative magnitude of value missing or value slippage.

### Compromised execution persistence (CEP)

Compromised execution persistence is the cumulative number of active compromised cell-steps across all governance cells, including the originating cell.

CEP captures the duration and extent of active compromised execution.

### Bounded-leakage gap

The bounded-leakage gap is defined as:

```text
G = Pr(L = 1) - Pr(C = 1)
  = Pr(L = 1, C = 0)
```

where `L` denotes cross-cell leakage and `C` denotes systemic contagion.

It is the unconditional proportion of simulated episodes in which an adverse executable condition reaches at least one secondary cell but does not reach at least two secondary cells within the observation horizon.

A larger bounded-leakage gap does not by itself imply better containment and should be interpreted jointly with leakage, systemic contagion, PE, CEP, and strategic velocity.

## Reference results

Across the full 196-condition design for each topology, the manuscript reports the following design-wide means:

| Scenario | Systemic contagion | Cross-cell leakage | PE | Strategic velocity |
|---|---:|---:|---:|---:|
| S0 | 3.12% | 12.84% | 0.170 | 97.35% |
| S1 | 0.29% | 4.26% | 0.046 | 99.26% |
| S2 | 1.43% | 12.84% | 0.144 | 97.61% |
| S3 | 0.95% | 7.14% | 0.082 | 98.68% |

The S0–S2 comparison is particularly important because both topologies give the originating cell direct access to all four secondary cells.

Cross-cell leakage is therefore identical across all 196 matched S0–S2 parameter conditions, while secondary-to-secondary escalation is structurally restricted under S2.

At the manuscript anchor condition:

```text
p   = 0.010
τ  = 5
FN  = 0.20
```

under S0:

```text
Cross-cell leakage  = 21.8%
Systemic contagion  = 4.2%
Bounded-leakage gap = 17.6 percentage points
```

Across the full parameter-sweep design, the mean bounded-leakage gaps are:

```text
S0 =  9.72 percentage points
S1 =  3.97 percentage points
S2 = 11.41 percentage points
S3 =  6.18 percentage points
```

These quantities are simulation outcomes within the specified stress-test design, not empirical estimates of real-world agentic-AI incident frequencies.

## Environment

The tested Python environment is recorded in `requirements.txt`.

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Full reproduction

Run the stochastic containment experiment:

```bash
python mge_simulation_full_robustness.py --replicates 1000 --seed 42
```

The final simulator should write a combined four-topology parameter-sweep file containing a scenario identifier for S0–S3.

Recommended output:

```text
simulation_output/parameter_sweep_4topologies.csv
```

Figure-generation and marginal-analysis scripts should consume this combined output and reproduce the manuscript figures and summary statistics.

The final repository should include numerical CSV outputs as the primary artifacts for computational comparison.

PDF and PNG figures may contain renderer- or metadata-dependent differences across software environments.

## Computational verification

The simulator should include boundary-condition checks verifying core implementation logic, including that:

- zero propagation probability prevents secondary propagation;
- immediate perfect mediation prevents propagation;
- certain propagation with complete detection failure can escape the originating cell;
- newly compromised cells do not propagate during the
