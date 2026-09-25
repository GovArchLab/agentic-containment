import os
import argparse
import pandas as pd


OUTCOMES = [
    "systemic_contagion_pct",
    "cross_cell_leakage_pct",
    "strategic_velocity_pct",
    "accumulated_value_missing",
    "value_slippage",
]

SHORT = {
    "systemic_contagion_pct": "Systemic",
    "cross_cell_leakage_pct": "Leakage",
    "strategic_velocity_pct": "Velocity",
    "accumulated_value_missing": "VM",
    "value_slippage": "VS",
}


def fmt(x, digits=2):
    return f"{x:.{digits}f}"


def compute_marginals(df):
    marginal_p = (
        df.groupby("p", as_index=False)[OUTCOMES]
        .mean()
    )

    marginal_tau = (
        df.groupby("tau", as_index=False)[OUTCOMES]
        .mean()
    )

    marginal_fn = (
        df.groupby("fn_rate", as_index=False)[OUTCOMES]
        .mean()
    )

    return marginal_p, marginal_tau, marginal_fn


def endpoint_contrast(table, factor):
    low = table.iloc[0]
    high = table.iloc[-1]

    result = {
        "factor": factor,
        "low": low[factor],
        "high": high[factor],
    }

    for outcome in OUTCOMES:
        result[f"{outcome}_low"] = low[outcome]
        result[f"{outcome}_high"] = high[outcome]
        result[f"{outcome}_delta"] = (
            high[outcome] - low[outcome]
        )

    return result


def make_main_paragraph(cp, ct, cf):
    """
    Create manuscript-ready LaTeX prose.

    Marginal means average over all combinations of the other two
    experimental parameters.
    """

    p = (
        "Averaging over all combinations of the other two parameters, "
        "propagation pressure produced the largest broad deterioration "
        "in containment outcomes. "
        f"Increasing \\(p\\) from {cp['low']:.3f} to {cp['high']:.3f} "
        f"changed mean systemic contagion from "
        f"\\({cp['systemic_contagion_pct_low']:.2f}\\%\\) to "
        f"\\({cp['systemic_contagion_pct_high']:.2f}\\%\\), "
        f"a difference of "
        f"\\({cp['systemic_contagion_pct_delta']:.2f}\\) percentage points, "
        f"while cross-cell leakage changed from "
        f"\\({cp['cross_cell_leakage_pct_low']:.2f}\\%\\) to "
        f"\\({cp['cross_cell_leakage_pct_high']:.2f}\\%\\)."
    )

    tau = (
        f" Increasing mediation delay from \\(\\tau={int(ct['low'])}\\) "
        f"to \\(\\tau={int(ct['high'])}\\) changed mean systemic contagion "
        f"from \\({ct['systemic_contagion_pct_low']:.2f}\\%\\) to "
        f"\\({ct['systemic_contagion_pct_high']:.2f}\\%\\) and reduced "
        f"mean strategic velocity from "
        f"\\({ct['strategic_velocity_pct_low']:.2f}\\%\\) to "
        f"\\({ct['strategic_velocity_pct_high']:.2f}\\%\\)."
    )

    fn = (
        f" Increasing the false-negative rate from "
        f"\\({cf['low'] * 100:.0f}\\%\\) to "
        f"\\({cf['high'] * 100:.0f}\\%\\) changed mean systemic contagion "
        f"from \\({cf['systemic_contagion_pct_low']:.2f}\\%\\) to "
        f"\\({cf['systemic_contagion_pct_high']:.2f}\\%\\) and "
        f"mean cross-cell leakage from "
        f"\\({cf['cross_cell_leakage_pct_low']:.2f}\\%\\) to "
        f"\\({cf['cross_cell_leakage_pct_high']:.2f}\\%\\)."
    )

    values = (
        " The value-related outcomes follow the same structural pattern "
        "but capture different mechanisms. "
        f"Across the low-to-high \\(p\\) contrast, propagated value-missing "
        f"exposure changed by "
        f"\\({cp['accumulated_value_missing_delta']:.3f}\\) "
        f"secondary-cell equivalents and value slippage by "
        f"\\({cp['value_slippage_delta']:.3f}\\) compromised cell-steps; "
        f"the corresponding delay contrasts were "
        f"\\({ct['accumulated_value_missing_delta']:.3f}\\) and "
        f"\\({ct['value_slippage_delta']:.3f}\\), and the detection-failure "
        f"contrasts were "
        f"\\({cf['accumulated_value_missing_delta']:.3f}\\) and "
        f"\\({cf['value_slippage_delta']:.3f}\\). "
        "These contrasts are descriptive marginal comparisons over the "
        "specified experimental grid rather than empirical effect estimates."
    )

    return p + tau + fn + values


def write_full_latex_table(
    marginal_p,
    marginal_tau,
    marginal_fn,
    path,
):
    rows = []

    for _, r in marginal_p.iterrows():
        rows.append(
            (
                f"$p={r['p']:.3f}$",
                r,
            )
        )

    for _, r in marginal_tau.iterrows():
        rows.append(
            (
                f"$\\tau={int(r['tau'])}$",
                r,
            )
        )

    for _, r in marginal_fn.iterrows():
        rows.append(
            (
                f"$\\mathrm{{FN}}={r['fn_rate'] * 100:.0f}\\%$",
                r,
            )
        )

    with open(path, "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n")
        f.write("\\centering\n")
        f.write(
            "\\caption{Marginal means across the parameter-sweep design.}\n"
        )
        f.write("\\label{tab:marginal-means}\n")
        f.write("\\begin{tabular}{lccccc}\n")
        f.write("\\hline\n")
        f.write(
            "Parameter & Systemic (\\%) & Leakage (\\%) & "
            "Velocity (\\%) & $VM$ & $VS$ \\\\\n"
        )
        f.write("\\hline\n")

        for label, r in rows:
            f.write(
                f"{label} & "
                f"{r['systemic_contagion_pct']:.2f} & "
                f"{r['cross_cell_leakage_pct']:.2f} & "
                f"{r['strategic_velocity_pct']:.2f} & "
                f"{r['accumulated_value_missing']:.3f} & "
                f"{r['value_slippage']:.3f} \\\\\n"
            )

        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write("\\begin{flushleft}\n")
        f.write("\\footnotesize\n")
        f.write(
            "Each marginal mean averages over all combinations of the "
            "other two experimental parameters. "
        )
        f.write(
            "Systemic denotes systemic contagion; Leakage denotes "
            "cross-cell leakage; Velocity denotes retained secondary-cell "
            "capacity; $VM$ denotes propagated value-missing exposure; "
            "$VS$ denotes value slippage in compromised cell-steps.\n"
        )
        f.write("\\end{flushleft}\n")
        f.write("\\end{table}\n")


def write_contrast_table(cp, ct, cf, path):
    """
    Compact table suitable for checking effect magnitude.
    Probably Supplementary, not main text.
    """

    rows = [
        (
            "$p: 0.001\\rightarrow0.020$",
            cp,
        ),
        (
            "$\\tau: 0\\rightarrow6$",
            ct,
        ),
        (
            "$\\mathrm{FN}: 0\\%\\rightarrow30\\%$",
            cf,
        ),
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n")
        f.write("\\centering\n")
        f.write(
            "\\caption{Low-to-high marginal contrasts across the "
            "parameter-sweep design.}\n"
        )
        f.write("\\label{tab:marginal-contrasts}\n")
        f.write("\\begin{tabular}{lccccc}\n")
        f.write("\\hline\n")
        f.write(
            "Parameter contrast & $\\Delta$Systemic & "
            "$\\Delta$Leakage & $\\Delta$Velocity & "
            "$\\Delta VM$ & $\\Delta VS$ \\\\\n"
        )
        f.write("\\hline\n")

        for label, c in rows:
            f.write(
                f"{label} & "
                f"{c['systemic_contagion_pct_delta']:+.2f} & "
                f"{c['cross_cell_leakage_pct_delta']:+.2f} & "
                f"{c['strategic_velocity_pct_delta']:+.2f} & "
                f"{c['accumulated_value_missing_delta']:+.3f} & "
                f"{c['value_slippage_delta']:+.3f} \\\\\n"
            )

        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write("\\begin{flushleft}\n")
        f.write("\\footnotesize\n")
        f.write(
            "Contrasts compare the highest and lowest tested value of "
            "each parameter after averaging over the other two parameters. "
        )
        f.write(
            "Systemic, Leakage, and Velocity differences are percentage "
            "points. "
        )
        f.write(
            "$VM$ is measured in secondary-cell equivalents and "
            "$VS$ in compromised cell-steps. "
        )
        f.write(
            "The contrasts are descriptive properties of the simulation "
            "design rather than causal or empirical effect estimates.\n"
        )
        f.write("\\end{flushleft}\n")
        f.write("\\end{table}\n")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="./simulation_output/parameter_sweep_196.csv",
    )

    parser.add_argument(
        "--outdir",
        default="./simulation_output/marginals",
    )

    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    df = pd.read_csv(args.input)

    required = {
        "p",
        "tau",
        "fn_rate",
        *OUTCOMES,
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    if len(df) != 196:
        raise ValueError(
            f"Expected 196 parameter conditions; found {len(df)}."
        )

    mp, mt, mf = compute_marginals(df)

    mp.to_csv(
        os.path.join(args.outdir, "marginal_by_p.csv"),
        index=False,
    )

    mt.to_csv(
        os.path.join(args.outdir, "marginal_by_tau.csv"),
        index=False,
    )

    mf.to_csv(
        os.path.join(args.outdir, "marginal_by_fn.csv"),
        index=False,
    )

    cp = endpoint_contrast(mp, "p")
    ct = endpoint_contrast(mt, "tau")
    cf = endpoint_contrast(mf, "fn_rate")

    paragraph = make_main_paragraph(
        cp,
        ct,
        cf,
    )

    paragraph_path = os.path.join(
        args.outdir,
        "marginal_effects_paragraph.tex",
    )

    with open(
        paragraph_path,
        "w",
        encoding="utf-8",
    ) as f:
        # one sentence per line for manuscript style
        for sentence in paragraph.split(". "):
            sentence = sentence.strip()
            if sentence:
                if not sentence.endswith("."):
                    sentence += "."
                f.write(sentence + "\n")

    write_full_latex_table(
        mp,
        mt,
        mf,
        os.path.join(
            args.outdir,
            "marginal_means_full.tex",
        ),
    )

    write_contrast_table(
        cp,
        ct,
        cf,
        os.path.join(
            args.outdir,
            "marginal_contrasts.tex",
        ),
    )

    print("\n=== MARGINAL MEANS BY p ===")
    print(mp.round(4).to_string(index=False))

    print("\n=== MARGINAL MEANS BY tau ===")
    print(mt.round(4).to_string(index=False))

    print("\n=== MARGINAL MEANS BY FN ===")
    print(mf.round(4).to_string(index=False))

    print("\n=== LOW-TO-HIGH MARGINAL CONTRASTS ===")

    for label, c in [
        ("p", cp),
        ("tau", ct),
        ("FN", cf),
    ]:
        print(
            f"{label:4s} | "
            f"Systemic {c['systemic_contagion_pct_delta']:+.2f} pp | "
            f"Leakage {c['cross_cell_leakage_pct_delta']:+.2f} pp | "
            f"Velocity {c['strategic_velocity_pct_delta']:+.2f} pp | "
            f"VM {c['accumulated_value_missing_delta']:+.3f} | "
            f"VS {c['value_slippage_delta']:+.3f}"
        )

    print("\n=== MANUSCRIPT PARAGRAPH ===\n")
    print(paragraph)

    print("\nFiles written to:", args.outdir)


if __name__ == "__main__":
    main()

    
