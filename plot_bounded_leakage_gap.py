"""
plot_bounded_leakage_gap.py

Generate the bounded-leakage-gap response surface for the
S0 Maximal-Connectivity Topology.

The bounded-leakage gap is:

    cross-cell leakage rate
    minus
    systemic contagion rate

and is reported in percentage points.

Input:
    ./simulation_output/
        S0_maximal_connectivity/
        parameter_sweep_196.csv

Outputs:
    ./figures/bounded_leakage_gap.pdf
    ./figures/bounded_leakage_gap.png

Optional:
    --annotate
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
# MAIN FIGURE FUNCTION
# ======================================================================

def make_bounded_leakage_gap(
    csv_path,
    outdir="./figures",
    annotate=False,
):

    if not (
        os.path.exists(
            csv_path
        )
    ):
        raise FileNotFoundError(
            "S0 simulation output not found:\n"
            f"{csv_path}"
        )


    df = pd.read_csv(
        csv_path
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


    os.makedirs(
        outdir,
        exist_ok=True,
    )


    # ==============================================================
    # BOUNDED-LEAKAGE GAP
    # ==============================================================

    df[
        "bounded_leakage_gap_pp"
    ] = (
        df[
            "cross_cell_leakage_pct"
        ]
        - df[
            "systemic_contagion_pct"
        ]
    )


    if (
        df[
            "bounded_leakage_gap_pp"
        ]
        < -1e-10
    ).any():

        raise ValueError(
            "Negative bounded-leakage gap detected. "
            "Check outcome definitions."
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


    observed_max = float(
        df[
            "bounded_leakage_gap_pp"
        ].max()
    )


    if observed_max <= 10:
        vmax = 10.0

    elif observed_max <= 20:
        vmax = 20.0

    elif observed_max <= 30:
        vmax = 30.0

    elif observed_max <= 40:
        vmax = 40.0

    else:
        vmax = (
            np.ceil(
                observed_max
                / 10.0
            )
            * 10.0
        )


    norm = Normalize(
        vmin=0.0,
        vmax=vmax,
    )


    cmap = (
        plt.cm.YlGnBu
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
                values=(
                    "bounded_leakage_gap_pp"
                ),
            )
            .reindex(
                index=tau_values,
                columns=fn_values,
            )
        )


        if (
            pivot
            .isna()
            .any()
            .any()
        ):
            raise RuntimeError(
                f"Incomplete bounded-leakage "
                f"surface for p={p:.3f}."
            )


        Z = (
            pivot.values
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


        candidate_levels = [
            5,
            10,
            15,
            20,
            25,
            30,
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
                    fontsize=6.3,
                    fmt=lambda x:
                        f"{x:.0f}",
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
        "Bounded leakage gap (percentage points)",
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

    suffix = (
        "_annotated"
        if annotate
        else ""
    )


    pdf_path = (
        os.path.join(
            outdir,
            f"bounded_leakage_gap{suffix}.pdf",
        )
    )


    png_path = (
        os.path.join(
            outdir,
            f"bounded_leakage_gap{suffix}.png",
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


    # ==============================================================
    # ANCHOR CONDITION
    # ==============================================================

    anchor = (
        df[
            np.isclose(
                df["p"],
                0.010,
            )
            & (
                df["tau"]
                == 5
            )
            & np.isclose(
                df[
                    "fn_rate"
                ],
                0.20,
            )
        ]
    )


    if len(anchor) == 1:

        row = (
            anchor.iloc[0]
        )


        print()
        print(
            "ANCHOR CONDITION"
        )

        print(
            "-" * 60
        )


        print(
            "Cross-cell leakage : "
            f"{row['cross_cell_leakage_pct']:.1f}%"
        )


        print(
            "Systemic contagion : "
            f"{row['systemic_contagion_pct']:.1f}%"
        )


        print(
            "Bounded leakage gap: "
            f"{row['bounded_leakage_gap_pp']:.1f} "
            "percentage points"
        )


    print()

    print(
        "Maximum bounded leakage gap: "
        f"{df['bounded_leakage_gap_pp'].max():.1f} "
        "percentage points"
    )


# ======================================================================
# COMMAND LINE
# ======================================================================

if __name__ == "__main__":

    parser = (
        argparse.ArgumentParser(
            description=(
                "Generate the S0 bounded-leakage-gap "
                "response surface."
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


    parser.add_argument(
        "--annotate",
        action="store_true",
        help=(
            "Print cell-level percentage-point "
            "values inside the heatmap."
        ),
    )


    args = (
        parser.parse_args()
    )


    make_bounded_leakage_gap(
        csv_path=(
            args.input
        ),
        outdir=(
            args.outdir
        ),
        annotate=(
            args.annotate
        ),
    )
    
