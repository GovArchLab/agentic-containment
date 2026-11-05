"""
plot_topology_stress_results.py

Generate the four-panel topology comparison figure for:

Governing Agentic AI Under Deep Uncertainty:
Scenario-Based Stress Tests of Institutional Containment

Input:
    ./simulation_output/scenario_sweep_784.csv

Output:
    ./figures/topology_stress_results.png
    ./figures/topology_stress_results.pdf
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ======================================================================
# PATHS
# ======================================================================

INPUT = Path(
    "./simulation_output/scenario_sweep_784.csv"
)

OUTDIR = Path(
    "./figures"
)

OUTDIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUTPUT_PNG = (
    OUTDIR
    / "topology_stress_results.png"
)

OUTPUT_PDF = (
    OUTDIR
    / "topology_stress_results.pdf"
)


# ======================================================================
# SCENARIOS
# ======================================================================

SCENARIO_ORDER = [
    "S0_maximal_connectivity",
    "S1_sparse_sequential",
    "S2_hub_mediated",
    "S3_layered",
]


SCENARIO_LABELS = {

    "S0_maximal_connectivity":
        "S0 Maximal-Connectivity Topology",

    "S1_sparse_sequential":
        "S1 Sparse Sequential Topology",

    "S2_hub_mediated":
        "S2 Hub-Mediated Topology",

    "S3_layered":
        "S3 Layered Topology",
}


COLORS = {

    "S0_maximal_connectivity":
        "#222222",

    "S1_sparse_sequential":
        "#1f77b4",

    "S2_hub_mediated":
        "#d62728",

    "S3_layered":
        "#2ca02c",
}


MARKERS = {

    "S0_maximal_connectivity":
        "o",

    "S1_sparse_sequential":
        "s",

    "S2_hub_mediated":
        "^",

    "S3_layered":
        "D",
}


# ======================================================================
# HELPERS
# ======================================================================

def grouped_mean(
    df,
    group_cols,
    value_cols,
):

    return (
        df.groupby(
            group_cols,
            as_index=False,
        )[value_cols]
        .mean()
        .copy()
    )


# ======================================================================
# MAIN
# ======================================================================

def main():

    if not INPUT.exists():
        raise FileNotFoundError(
            "Combined simulation output not found:\n"
            f"{INPUT}\n\n"
            "Run institutional_containment_stress_test.py first."
        )


    df = pd.read_csv(
        INPUT
    )


    if len(df) != 784:
        raise RuntimeError(
            f"Expected 784 rows; obtained {len(df)}."
        )


    observed = set(
        df[
            "scenario_id"
        ].unique()
    )

    expected = set(
        SCENARIO_ORDER
    )

    if observed != expected:
        raise RuntimeError(
            "Unexpected scenario IDs.\n\n"
            f"Expected: {sorted(expected)}\n"
            f"Observed: {sorted(observed)}"
        )


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


    value_columns = [
        "systemic_contagion_pct",
        "cross_cell_leakage_pct",
        "strategic_velocity_pct",
        "propagated_exposure",
        "compromised_execution_persistence",
        "bounded_leakage_gap_pp",
    ]


    by_p = grouped_mean(
        df,
        [
            "scenario_id",
            "p",
        ],
        value_columns,
    )


    by_tau = grouped_mean(
        df,
        [
            "scenario_id",
            "tau",
        ],
        value_columns,
    )


    by_fn = grouped_mean(
        df,
        [
            "scenario_id",
            "fn_rate",
        ],
        value_columns,
    )


    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "legend.fontsize": 9.2,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )


    fig, axes = plt.subplots(
        2,
        2,
        figsize=(
            12,
            8,
        ),
        constrained_layout=True,
    )


    # ==============================================================
    # PANEL A
    # Systemic contagion vs propagation pressure
    # ==============================================================

    ax = axes[
        0,
        0,
    ]


    for scenario in (
        SCENARIO_ORDER
    ):

        part = (
            by_p[
                by_p[
                    "scenario_id"
                ]
                == scenario
            ]
            .sort_values(
                "p"
            )
        )


        ax.plot(
            part["p"],
            part[
                "systemic_contagion_pct"
            ],
            label=(
                SCENARIO_LABELS[
                    scenario
                ]
            ),
            color=(
                COLORS[
                    scenario
                ]
            ),
            marker=(
                MARKERS[
                    scenario
                ]
            ),
            linewidth=2,
            markersize=6,
        )


    ax.set_title(
        "(A) Systemic contagion across propagation pressure"
    )

    ax.set_xlabel(
        "Propagation probability p"
    )

    ax.set_ylabel(
        "Mean systemic contagion (%)"
    )

    ax.grid(
        True,
        alpha=0.3,
    )


    # ==============================================================
    # PANEL B
    # Cross-cell leakage vs propagation pressure
    # ==============================================================

    ax = axes[
        0,
        1,
    ]


    for scenario in (
        SCENARIO_ORDER
    ):

        part = (
            by_p[
                by_p[
                    "scenario_id"
                ]
                == scenario
            ]
            .sort_values(
                "p"
            )
        )


        ax.plot(
            part["p"],
            part[
                "cross_cell_leakage_pct"
            ],
            label=(
                SCENARIO_LABELS[
                    scenario
                ]
            ),
            color=(
                COLORS[
                    scenario
                ]
            ),
            marker=(
                MARKERS[
                    scenario
                ]
            ),
            linewidth=2,
            markersize=6,
        )


    ax.set_title(
        "(B) Cross-cell leakage across propagation pressure"
    )

    ax.set_xlabel(
        "Propagation probability p"
    )

    ax.set_ylabel(
        "Mean cross-cell leakage (%)"
    )

    ax.grid(
        True,
        alpha=0.3,
    )


    # ==============================================================
    # PANEL C
    # CEP vs mediation delay
    # ==============================================================

    ax = axes[
        1,
        0,
    ]


    for scenario in (
        SCENARIO_ORDER
    ):

        part = (
            by_tau[
                by_tau[
                    "scenario_id"
                ]
                == scenario
            ]
            .sort_values(
                "tau"
            )
        )


        ax.plot(
            part["tau"],
            part[
                "compromised_execution_persistence"
            ],
            label=(
                SCENARIO_LABELS[
                    scenario
                ]
            ),
            color=(
                COLORS[
                    scenario
                ]
            ),
            marker=(
                MARKERS[
                    scenario
                ]
            ),
            linewidth=2,
            markersize=6,
        )


    ax.set_title(
        "(C) Compromised execution persistence across mediation delay"
    )

    ax.set_xlabel(
        r"Mediation delay $\tau$ (simulation steps)"
    )

    ax.set_ylabel(
        "Mean compromised execution persistence"
    )

    ax.grid(
        True,
        alpha=0.3,
    )


    # ==============================================================
    # PANEL D
    # Systemic contagion vs episode-level non-detection
    # ==============================================================

    ax = axes[
        1,
        1,
    ]


    for scenario in (
        SCENARIO_ORDER
    ):

        part = (
            by_fn[
                by_fn[
                    "scenario_id"
                ]
                == scenario
            ]
            .sort_values(
                "fn_rate"
            )
        )


        ax.plot(
            part[
                "fn_rate"
            ],
            part[
                "systemic_contagion_pct"
            ],
            label=(
                SCENARIO_LABELS[
                    scenario
                ]
            ),
            color=(
                COLORS[
                    scenario
                ]
            ),
            marker=(
                MARKERS[
                    scenario
                ]
            ),
            linewidth=2,
            markersize=6,
        )


    ax.set_title(
        "(D) Systemic contagion across non-detection"
    )

    ax.set_xlabel(
        "Episode-level non-detection probability FN"
    )

    ax.set_ylabel(
        "Mean systemic contagion (%)"
    )

    ax.grid(
        True,
        alpha=0.3,
    )


    # ==============================================================
    # SHARED LEGEND
    # ==============================================================

    handles, labels = (
        axes[
            0,
            0,
        ]
        .get_legend_handles_labels()
    )


    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(
            0.5,
            1.055,
        ),
        columnspacing=1.8,
        handletextpad=0.6,
    )


    fig.suptitle(
        "Scenario-Based Stress Tests of Institutional Containment",
        fontsize=13,
        y=1.10,
    )


    # ==============================================================
    # SAVE
    # ==============================================================

    fig.savefig(
        OUTPUT_PNG,
        dpi=600,
        bbox_inches="tight",
    )


    fig.savefig(
        OUTPUT_PDF,
        bbox_inches="tight",
    )


    plt.close(
        fig
    )


    print(
        f"Saved PNG: {OUTPUT_PNG}"
    )

    print(
        f"Saved PDF: {OUTPUT_PDF}"
    )


if __name__ == "__main__":
    main()
    
