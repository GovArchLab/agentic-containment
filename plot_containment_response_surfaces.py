"""
plot_containment_response_surfaces.py

Generate response-surface figures for the S0
Maximal-Connectivity Topology.

The figures show systemic contagion and cross-cell leakage
across mediation delay and episode-level non-detection
for each tested propagation-pressure value.

Input:
    ./simulation_output/
        S0_maximal_connectivity/
        parameter_sweep_196.csv

Outputs:
    ./figures/containment_envelope.*
    ./figures/leakage_envelope.*
    ./figures/containment_envelope_clean.*
    ./figures/leakage_envelope_clean.*
"""

import argparse
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.colors import Normalize


P_VALUES = [
    0.001,
    0.005,
    0.010,
    0.020,
]


# ======================================================================
# MATRIX PREPARATION
# ======================================================================

def prepare_matrix(
    df,
    p,
    value_col,
    tau_values,
    fn_values,
):

    sub = (
        df[
            np.isclose(
                df["p"],
                p,
            )
        ]
        .copy()
    )


    pivot = (
        sub.pivot(
            index="tau",
            columns="fn_rate",
            values=value_col,
        )
        .reindex(
            index=tau_values,
            columns=fn_values,
        )
    )


    if pivot.isna().any().any():
        raise RuntimeError(
            f"Incomplete response surface for p={p:.3f} "
            f"and outcome {value_col}."
        )


    return (
        pivot.values
    )


# ======================================================================
# FOUR-PANEL HEATMAP
# ======================================================================

def make_four_panel_heatmap(
    df,
    value_col,
    output_base,
    colorbar_label,
    annotate=True,
    contour=True,
    outdir="./figures",
):

    os.makedirs(
        outdir,
        exist_ok=True,
    )


    tau_values = sorted(
        df[
            "tau"
        ].unique()
    )


    fn_values = sorted(
        df[
            "fn_rate"
        ].unique()
    )


    vmin = 0.0


    observed_max = float(
        df[
            value_col
        ].max()
    )


    if observed_max <= 10:
        vmax = 10.0

    elif observed_max <= 20:
        vmax = 20.0

    elif observed_max <= 30:
        vmax = 30.0

    elif observed_max <= 50:
        vmax = 50.0

    else:
        vmax = (
            np.ceil(
                observed_max
                / 10.0
            )
            * 10.0
        )


    fig, axes = plt.subplots(
        2,
        2,
        figsize=(
            7.2,
            5.8,
        ),
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )


    axes = (
        axes.flatten()
    )


    norm = Normalize(
        vmin=vmin,
        vmax=vmax,
    )


    cmap = (
        plt.cm.Blues
    )


    image = None


    for panel_no, (
        ax,
        p,
    ) in enumerate(
        zip(
            axes,
            P_VALUES,
        )
    ):

        Z = prepare_matrix(
            df=df,
            p=p,
            value_col=value_col,
            tau_values=tau_values,
            fn_values=fn_values,
        )


        image = ax.imshow(
            Z,
            origin="lower",
            aspect="auto",
            cmap=cmap,
            norm=norm,
            interpolation="nearest",
        )


        panel_letter = chr(
            ord("A")
            + panel_no
        )


        ax.set_title(
            rf"$\bf{{{panel_letter}}}$   "
            rf"$p={p:.3f}$",
            fontsize=9.5,
            loc="left",
            pad=5,
        )


        ax.set_xticks(
            np.arange(
                len(
                    fn_values
                )
            )
        )


        ax.set_xticklabels(
            [
                f"{int(fn * 100)}"
                for fn
                in fn_values
            ],
            fontsize=8,
        )


        ax.set_yticks(
            np.arange(
                len(
                    tau_values
                )
            )
        )


        ax.set_yticklabels(
            [
                str(
                    int(tau)
                )
                for tau
                in tau_values
            ],
            fontsize=8,
        )


        # Fine cell boundaries.
        ax.set_xticks(
            np.arange(
                -0.5,
                len(fn_values),
                1,
            ),
            minor=True,
        )


        ax.set_yticks(
            np.arange(
                -0.5,
                len(tau_values),
                1,
            ),
            minor=True,
        )


        ax.grid(
            which="minor",
            color="white",
            linestyle="-",
            linewidth=0.55,
            alpha=0.80,
        )


        ax.tick_params(
            which="minor",
            bottom=False,
            left=False,
        )


        ax.tick_params(
            which="major",
            length=2.5,
            width=0.6,
        )


        # ----------------------------------------------------------
        # OPTIONAL CELL VALUES
        # ----------------------------------------------------------

        if annotate:

            for i in range(
                len(
                    tau_values
                )
            ):

                for j in range(
                    len(
                        fn_values
                    )
                ):

                    value = (
                        Z[
                            i,
                            j,
                        ]
                    )


                    rgba = (
                        cmap(
                            norm(
                                value
                            )
                        )
                    )


                    luminance = (
                        0.299
                        * rgba[0]
                        + 0.587
                        * rgba[1]
                        + 0.114
                        * rgba[2]
                    )


                    text_color = (
                        "white"
                        if luminance < 0.55
                        else "black"
                    )


                    ax.text(
                        j,
                        i,
                        f"{value:.1f}",
                        ha="center",
                        va="center",
                        fontsize=6.3,
                        color=text_color,
                    )


        # ----------------------------------------------------------
        # CONTOURS
        # ----------------------------------------------------------

        if contour:

            X, Y = (
                np.meshgrid(
                    np.arange(
                        len(
                            fn_values
                        )
                    ),
                    np.arange(
                        len(
                            tau_values
                        )
                    ),
                )
            )


            if (
                value_col
                == "systemic_contagion_pct"
            ):

                candidate_levels = [
                    5,
                    10,
                    15,
                ]

            else:

                candidate_levels = [
                    10,
                    20,
                    30,
                    40,
                ]


            valid_levels = [
                level
                for level
                in candidate_levels
                if (
                    np.nanmin(Z)
                    < level
                    < np.nanmax(Z)
                )
            ]


            if valid_levels:

                cs = ax.contour(
                    X,
                    Y,
                    Z,
                    levels=(
                        valid_levels
                    ),
                    colors="black",
                    linewidths=0.55,
                    alpha=0.65,
                )


                if not annotate:

                    ax.clabel(
                        cs,
                        inline=True,
                        fontsize=6.5,
                        fmt=lambda x:
                            f"{x:.0f}%",
                    )


        for spine in (
            ax.spines.values()
        ):

            spine.set_linewidth(
                0.6
            )


    # ==============================================================
    # SHARED LABELS
    # ==============================================================

    fig.supxlabel(
        "Episode-level non-detection probability, FN (%)",
        fontsize=9,
    )


    fig.supylabel(
        r"Mediation delay $\tau$ (simulation steps)",
        fontsize=9,
    )


    cbar = fig.colorbar(
        image,
        ax=axes,
        fraction=0.035,
        pad=0.025,
    )


    cbar.set_label(
        colorbar_label,
        fontsize=8.5,
    )


    cbar.ax.tick_params(
        labelsize=7.5,
        length=2.5,
        width=0.6,
    )


    cbar.outline.set_linewidth(
        0.6
    )


    # ==============================================================
    # SAVE
    # ==============================================================

    pdf_path = (
        os.path.join(
            outdir,
            f"{output_base}.pdf",
        )
    )


    png_path = (
        os.path.join(
            outdir,
            f"{output_base}.png",
        )
    )


    fig.savefig(
        pdf_path,
        format="pdf",
        bbox_inches="tight",
    )


    fig.savefig(
        png_path,
        format="png",
        dpi=600,
        bbox_inches="tight",
    )


    plt.close(
        fig
    )


    print(
        f"Saved PDF: {pdf_path}"
    )

    print(
        f"Saved PNG: {png_path}"
    )


# ======================================================================
# MAIN
# ======================================================================

def main():

    parser = (
        argparse.ArgumentParser(
            description=(
                "Generate S0 systemic-contagion "
                "and cross-cell-leakage "
                "response surfaces."
            )
        )
    )


    parser.add_argument(
        "--input",
        type=str,
        default=(
            "./simulation_output/"
            "S0_maximal_connectivity/"
            "parameter_sweep_196.csv"
        ),
    )


    parser.add_argument(
        "--outdir",
        type=str,
        default="./figures",
    )


    args = (
        parser.parse_args()
    )


    if not (
        os.path.exists(
            args.input
        )
    ):
        raise FileNotFoundError(
            "S0 simulation output not found:\n"
            f"{args.input}"
        )


    df = pd.read_csv(
        args.input
    )


    if len(df) != 196:
        raise RuntimeError(
            f"Expected 196 S0 rows; obtained {len(df)}."
        )


    required = {
        "p",
        "tau",
        "fn_rate",
        "systemic_contagion_pct",
        "cross_cell_leakage_pct",
    }


    missing = (
        required
        - set(
            df.columns
        )
    )


    if missing:
        raise ValueError(
            "Missing required columns:\n"
            f"{sorted(missing)}"
        )


    # --------------------------------------------------------------
    # SYSTEMIC CONTAGION ? annotated
    # --------------------------------------------------------------

    make_four_panel_heatmap(
        df=df,
        value_col=(
            "systemic_contagion_pct"
        ),
        output_base=(
            "containment_envelope"
        ),
        colorbar_label=(
            "Systemic contagion rate (%)"
        ),
        annotate=True,
        contour=True,
        outdir=args.outdir,
    )


    # --------------------------------------------------------------
    # CROSS-CELL LEAKAGE ? annotated
    # --------------------------------------------------------------

    make_four_panel_heatmap(
        df=df,
        value_col=(
            "cross_cell_leakage_pct"
        ),
        output_base=(
            "leakage_envelope"
        ),
        colorbar_label=(
            "Cross-cell leakage rate (%)"
        ),
        annotate=True,
        contour=True,
        outdir=args.outdir,
    )


    # --------------------------------------------------------------
    # SYSTEMIC CONTAGION ? clean publication version
    # --------------------------------------------------------------

    make_four_panel_heatmap(
        df=df,
        value_col=(
            "systemic_contagion_pct"
        ),
        output_base=(
            "containment_envelope_clean"
        ),
        colorbar_label=(
            "Systemic contagion rate (%)"
        ),
        annotate=False,
        contour=True,
        outdir=args.outdir,
    )


    # --------------------------------------------------------------
    # CROSS-CELL LEAKAGE ? clean publication version
    # --------------------------------------------------------------

    make_four_panel_heatmap(
        df=df,
        value_col=(
            "cross_cell_leakage_pct"
        ),
        output_base=(
            "leakage_envelope_clean"
        ),
        colorbar_label=(
            "Cross-cell leakage rate (%)"
        ),
        annotate=False,
        contour=True,
        outdir=args.outdir,
    )


if __name__ == "__main__":
    main()
    
