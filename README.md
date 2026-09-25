# Regulating the Unknowns of Agentic AI — Reproducibility Code

This repository contains the simulation and figure-generation code associated with the manuscript:

**Regulating the Unknowns of Agentic AI: Institutional Containment and Runtime Mediation of Value Missing and Value Slippage**

The code implements the stochastic containment experiment used to examine how a governance-cell architecture responds after an adverse executable condition has emerged.

## Scope

The simulation is a **structured stochastic design experiment**. It is not calibrated to empirical frequencies of real-world agentic-AI failure and should not be interpreted as an estimator of such frequencies.

The experiment varies three parameters:

- propagation probability, `p ∈ {0.001, 0.005, 0.010, 0.020}`;
- mediation delay, `tau ∈ {0, 1, 2, 3, 4, 5, 6}`;
- episode-level non-detection probability, `FN ∈ {0.00, 0.05, ..., 0.30}`.

This produces `4 × 7 × 7 = 196` parameter conditions. The manuscript results use 1,000 Monte Carlo replications per condition and random seed 42, for 196,000 stochastic runs.

The model fixes the number of governance cells at five and the observation horizon at 12 simulation steps.

## Main outcomes

The simulation reports the following outcomes.

- **Systemic contagion**: compromise reaches at least two secondary governance cells beyond the originating cell.
- **Cross-cell leakage**: compromise reaches at least one secondary governance cell.
- **Strategic velocity**: percentage of secondary cell-capacity remaining uncompromised across the observation window.
- **Propagated Exposure (PE)**: mean number of secondary governance cells reached by the adverse executable condition.
- **Compromised Execution Persistence (CEP)**: mean cumulative active compromised cell-steps across the observation window.

PE and CEP are downstream consequences of an adverse executable condition. They are not measures of value missing or value slippage.

## Repository structure

```text
.
├── mge_simulation_full_robustness.py
├── make_containment_envelope.py
├── make_bounded_leakage_gap.py
├── make_marginal_effects.py
├── requirements.txt
├── README.md
├── CITATION.cff
├── LICENSE
├── scripts/
│   └── replay_for_README.ps1
├── tools/
│   └── audit_mge_terminology.py
├── simulation_output/
│   ├── parameter_sweep_196.csv
│   ├── simulation_manifest.json
│   ├── marginal_by_p.csv
│   ├── marginal_by_tau.csv
│   ├── marginal_by_fn.csv
│   ├── forensic_registry/
│   │   └── illustrative_action_trace.json
│   └── marginals/
│       ├── marginal_by_p.csv
│       ├── marginal_by_tau.csv
│       ├── marginal_by_fn.csv
│       ├── marginal_effects_paragraph.tex
│       ├── marginal_means_full.tex
│       └── marginal_contrasts.tex
└── figures/
    ├── containment_envelope.pdf
    ├── containment_envelope.png
    ├── bounded_leakage_gap.pdf
    ├── bounded_leakage_gap.png
    ├── bounded_leakage_gap_annotated.pdf
    └── bounded_leakage_gap_annotated.png
```

## Environment

A tested Python environment is recorded in `requirements.txt`.

Create and activate a virtual environment, then install the dependencies:

```text
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```text
.\.venv\Scripts\Activate.ps1
```

## Full reproduction

Run the stochastic experiment:

```text
python mge_simulation_full_robustness.py --replicates 1000 --seed 42
```

Generate the containment-envelope figure:

```text
python make_containment_envelope.py --input ./simulation_output/parameter_sweep_196.csv --outdir ./figures
```

Generate the clean bounded-leakage-gap figure:

```text
python make_bounded_leakage_gap.py --input ./simulation_output/parameter_sweep_196.csv --outdir ./figures
```

Generate the annotated supplementary version:

```text
python make_bounded_leakage_gap.py --input ./simulation_output/parameter_sweep_196.csv --outdir ./figures --annotate
```

Generate the manuscript marginal summaries and LaTeX artifacts:

```text
python make_marginal_effects.py --input ./simulation_output/parameter_sweep_196.csv
```

Windows users can run the complete sequence with:

```text
.\scripts\replay_for_README.ps1
```

## Expected reference results

For the manuscript anchor condition

```text
p = 0.010
tau = 5
FN = 0.20
```

the expected output is:

```text
Systemic contagion    : 4.20%
Strategic velocity    : 95.80%
Propagated exposure   : 0.270 secondary cells
CEP                   : 7.872 compromised cell-steps
Cross-cell leakage    : 21.8%
Bounded leakage gap   : 17.6 percentage points
```

The maximum bounded leakage gap across the experimental grid is:

```text
24.0 percentage points
```

The expected low-to-high marginal contrasts are:

| Parameter | Systemic contagion | Cross-cell leakage | Strategic velocity | PE | CEP |
|---|---:|---:|---:|---:|---:|
| `p` | +8.92 pp | +23.50 pp | -5.41 pp | +0.359 | +1.452 |
| `tau` | +5.58 pp | +16.23 pp | -3.73 pp | +0.241 | +6.629 |
| `FN` | +2.18 pp | +6.59 pp | -0.82 pp | +0.096 | +3.145 |

These are descriptive marginal comparisons over the specified experimental grid, not empirical effect estimates.

## Generated outputs

`mge_simulation_full_robustness.py` writes the main stochastic results to:

```text
simulation_output/parameter_sweep_196.csv
```

It also writes:

```text
simulation_output/simulation_manifest.json
simulation_output/marginal_by_p.csv
simulation_output/marginal_by_tau.csv
simulation_output/marginal_by_fn.csv
simulation_output/forensic_registry/illustrative_action_trace.json
```

`make_marginal_effects.py` writes the manuscript-oriented marginal analyses to:

```text
simulation_output/marginals/
```

The root-level marginal CSVs and the files under `simulation_output/marginals/` serve different purposes. The latter include cross-cell leakage and the LaTeX artifacts used for manuscript reporting.

## Reproducibility notes

The simulator reinitializes the pseudorandom generator with seed 42 for each parameter condition. This implements common random numbers across conditions and reduces irrelevant Monte Carlo variation in comparisons across the response surface.

A newly compromised cell becomes active at the following simulation step. With `tau = 0`, a successfully detected newly compromised cell is isolated before its first propagation opportunity.

The illustrative Action Trace contains a UTC timestamp. Its `sha256_integrity_anchor` is therefore regenerated on each run. A different Action Trace file hash across runs does not imply a change in the stochastic simulation.

PDF files may also contain renderer- or metadata-dependent differences across software environments. Numerical CSV outputs are the primary artifacts for computational comparison.

## Computational verification

The simulator includes boundary-condition checks that verify implementation logic, including:

- zero propagation probability prevents secondary propagation;
- immediate perfect mediation prevents propagation;
- certain propagation with complete detection failure escapes the originating cell.

These checks are computational verification, not empirical validation.

The public terminology audit can be run with:

```text
python tools/audit_mge_terminology.py
```

## License

The code is released under the MIT License. See `LICENSE`.

## Citation

Citation metadata are provided in `CITATION.cff`.

The repository currently preserves anonymous authorship to remain consistent with the anonymized manuscript. Replace the anonymous author entry in `CITATION.cff` and the copyright-holder line in `LICENSE` before a deanonymized public release.
