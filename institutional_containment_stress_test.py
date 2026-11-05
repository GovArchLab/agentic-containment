"""
institutional_containment_stress_test.py

Reproducibility code for:

Governing Agentic AI Under Deep Uncertainty:
Scenario-Based Stress Tests of Institutional Containment

Purpose
-------
This standalone script reproduces the four-topology stochastic
stress test reported in the manuscript.

The experiment compares:

    S0: Maximal-Connectivity Topology
    S1: Sparse Sequential Topology
    S2: Hub-Mediated Topology
    S3: Layered Topology

for:

    p   in {0.001, 0.005, 0.010, 0.020}
    tau in {0, 1, 2, 3, 4, 5, 6}
    FN  in {0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30}

with 1,000 Monte Carlo replications per topology-condition
by default.

Reproducibility gate
--------------------
The topology-aware implementation must first reproduce the
previously verified S0 maximal-connectivity output exactly
for all 196 parameter conditions.

S1-S3 are executed only after this exact regression test passes.

Interpretation
--------------
The scenarios are theory-grounded synthetic stress environments.

They are not empirical case studies, calibrated forecasts,
or estimates of real-world agentic-AI incident frequencies.

Value missing and value slippage are possible conceptual sources
of an adverse executable condition, but are not stochastic inputs
to the propagation model.
"""

import argparse
import json
import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent

# ======================================================================
# EXPERIMENT CONSTANTS
# ======================================================================

NUM_CELLS = 5

P_VALUES = (
    0.001,
    0.005,
    0.010,
    0.020,
)

TAU_VALUES = (
    0,
    1,
    2,
    3,
    4,
    5,
    6,
)

FN_VALUES = (
    0.00,
    0.05,
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
)


# ======================================================================
# TOPOLOGIES
# ======================================================================

def complete_directed_edges(n):
    return tuple(
        (i, j)
        for i in range(n)
        for j in range(n)
        if i != j
    )


TOPOLOGIES = {

    "S0_maximal_connectivity": {
        "formal_name": (
            "Maximal-Connectivity Topology"
        ),
        "legacy_experiment_id": (
            "S0_maximal_connectivity"
        ),
        "topology_type": (
            "complete_directed"
        ),
        "interpretation": (
            "Every governance cell has a directed "
            "executable-authority interface to each "
            "of the other four cells."
        ),
        "origin_cell": 0,
        "cell_labels": (
            "Originating Governance Cell",
            "Secondary Governance Cell 1",
            "Secondary Governance Cell 2",
            "Secondary Governance Cell 3",
            "Secondary Governance Cell 4",
        ),
        "edges": (
            complete_directed_edges(
                NUM_CELLS
            )
        ),
    },

    "S1_sparse_sequential": {
        "formal_name": (
            "Sparse Sequential Topology"
        ),
        "legacy_experiment_id": (
            "S1_procurement"
        ),
        "topology_type": (
            "sparse_sequential"
        ),
        "interpretation": (
            "A sparse procurement-to-payment "
            "authority structure with limited "
            "immediate reach from the originating cell."
        ),
        "origin_cell": 0,
        "cell_labels": (
            "Supplier Intelligence",
            "Procurement Authorization",
            "Vendor Master",
            "Payment Execution",
            "Accounting and Compliance",
        ),
        "edges": (
            (0, 1),
            (1, 2),
            (1, 3),
            (2, 3),
            (3, 4),
        ),
    },

    "S2_hub_mediated": {
        "formal_name": (
            "Hub-Mediated Topology"
        ),
        "legacy_experiment_id": (
            "S2_tool_cascade"
        ),
        "topology_type": (
            "hub_mediated"
        ),
        "interpretation": (
            "The originating orchestration cell has "
            "bidirectional interfaces with each "
            "secondary domain, while secondary domains "
            "lack direct interfaces to one another."
        ),
        "origin_cell": 0,
        "cell_labels": (
            "Agent Orchestration",
            "Internal Data Services",
            "Communications",
            "External APIs and Services",
            "Privileged Enterprise Operations",
        ),
        "edges": (
            (0, 1),
            (1, 0),
            (0, 2),
            (2, 0),
            (0, 3),
            (3, 0),
            (0, 4),
            (4, 0),
        ),
    },

    "S3_layered": {
        "formal_name": (
            "Layered Topology"
        ),
        "legacy_experiment_id": (
            "S3_authorization_degradation"
        ),
        "topology_type": (
            "layered_directed"
        ),
        "interpretation": (
            "A layered structure in which adverse "
            "execution can acquire downstream "
            "consequences through successive "
            "institutional domains."
        ),
        "origin_cell": 0,
        "cell_labels": (
            "Customer Operations",
            "Customer Data",
            "Analytics and Decision Support",
            "External Disclosure and Partner Transfer",
            "Compliance and Oversight",
        ),
        "edges": (
            (0, 1),
            (0, 2),
            (1, 2),
            (1, 3),
            (2, 3),
            (2, 4),
            (3, 4),
        ),
    },
}


SCENARIO_ORDER = (
    "S0_maximal_connectivity",
    "S1_sparse_sequential",
    "S2_hub_mediated",
    "S3_layered",
)


# ======================================================================
# TOPOLOGY HELPERS
# ======================================================================

def build_adjacency_matrix(spec):

    matrix = np.zeros(
        (NUM_CELLS, NUM_CELLS),
        dtype=np.int64,
    )

    for source, target in spec["edges"]:

        if source == target:
            raise ValueError(
                "Self-edges are not allowed."
            )

        if not (
            0 <= source < NUM_CELLS
            and 0 <= target < NUM_CELLS
        ):
            raise ValueError(
                f"Invalid topology edge: "
                f"{(source, target)}"
            )

        matrix[
            source,
            target,
        ] = 1

    return matrix


def topology_metadata(
    scenario_id,
):

    spec = TOPOLOGIES[
        scenario_id
    ]

    adjacency = (
        build_adjacency_matrix(
            spec
        )
    )

    directed_edges = int(
        adjacency.sum()
    )

    possible_edges = (
        NUM_CELLS
        * (NUM_CELLS - 1)
    )

    density = (
        directed_edges
        / possible_edges
    )

    origin = (
        spec["origin_cell"]
    )

    origin_out_degree = int(
        adjacency[
            origin
        ].sum()
    )

    return {
        "scenario_id": (
            scenario_id
        ),
        "scenario_name": (
            spec["formal_name"]
        ),
        "legacy_experiment_id": (
            spec[
                "legacy_experiment_id"
            ]
        ),
        "topology_type": (
            spec["topology_type"]
        ),
        "directed_edges": (
            directed_edges
        ),
        "topology_density": (
            density
        ),
        "origin_out_degree": (
            origin_out_degree
        ),
        "origin_cell_label": (
            spec[
                "cell_labels"
            ][origin]
        ),
    }


def validate_topologies():

    expected_edges = {
        "S0_maximal_connectivity": 20,
        "S1_sparse_sequential": 5,
        "S2_hub_mediated": 8,
        "S3_layered": 7,
    }

    expected_origin_out_degree = {
        "S0_maximal_connectivity": 4,
        "S1_sparse_sequential": 1,
        "S2_hub_mediated": 4,
        "S3_layered": 2,
    }

    for scenario_id in SCENARIO_ORDER:

        spec = TOPOLOGIES[
            scenario_id
        ]

        if (
            len(
                spec[
                    "cell_labels"
                ]
            )
            != NUM_CELLS
        ):
            raise RuntimeError(
                f"{scenario_id}: "
                "incorrect number of "
                "cell labels."
            )

        adjacency = (
            build_adjacency_matrix(
                spec
            )
        )

        if not np.all(
            np.diag(
                adjacency
            )
            == 0
        ):
            raise RuntimeError(
                f"{scenario_id}: "
                "self-edge detected."
            )

        if int(
            adjacency.sum()
        ) != expected_edges[
            scenario_id
        ]:
            raise RuntimeError(
                f"{scenario_id}: "
                "unexpected edge count."
            )

        origin = (
            spec["origin_cell"]
        )

        if int(
            adjacency[
                origin
            ].sum()
        ) != (
            expected_origin_out_degree[
                scenario_id
            ]
        ):
            raise RuntimeError(
                f"{scenario_id}: "
                "unexpected origin "
                "out-degree."
            )

        # Verify reachability from origin.
        reached = {
            origin
        }

        frontier = {
            origin
        }

        while frontier:

            next_frontier = set()

            for source in frontier:

                targets = np.where(
                    adjacency[
                        source
                    ]
                    == 1
                )[0]

                for target in targets:

                    target = int(
                        target
                    )

                    if (
                        target
                        not in reached
                    ):
                        reached.add(
                            target
                        )

                        next_frontier.add(
                            target
                        )

            frontier = (
                next_frontier
            )

        if (
            len(reached)
            != NUM_CELLS
        ):
            raise RuntimeError(
                f"{scenario_id}: "
                "not all cells are "
                "reachable from origin."
            )


# ======================================================================
# SIMULATOR
# ======================================================================

class InstitutionalContainmentStressTest:

    def __init__(
        self,
        scenario_id,
        num_replicates=1000,
        sweep_horizon=12,
        systemic_secondary_threshold=2,
        seed=42,
    ):

        if (
            scenario_id
            not in TOPOLOGIES
        ):
            raise ValueError(
                f"Unknown scenario: "
                f"{scenario_id}"
            )

        if num_replicates < 1:
            raise ValueError(
                "num_replicates must "
                "be positive."
            )

        if sweep_horizon < 1:
            raise ValueError(
                "sweep_horizon must "
                "be positive."
            )

        if not (
            1
            <= systemic_secondary_threshold
            <= NUM_CELLS - 1
        ):
            raise ValueError(
                "Invalid systemic "
                "contagion threshold."
            )

        self.scenario_id = (
            scenario_id
        )

        self.scenario_spec = (
            TOPOLOGIES[
                scenario_id
            ]
        )

        self.adjacency = (
            build_adjacency_matrix(
                self.scenario_spec
            )
        )

        self.num_cells = (
            NUM_CELLS
        )

        self.num_replicates = (
            num_replicates
        )

        self.sweep_horizon = (
            sweep_horizon
        )

        self.systemic_secondary_threshold = (
            systemic_secondary_threshold
        )

        self.seed = seed

    # ------------------------------------------------------------------
    # STATISTICAL HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _mean_mcse(
        values,
    ):

        values = np.asarray(
            values,
            dtype=float,
        )

        mean = float(
            np.mean(
                values
            )
        )

        if (
            len(values)
            <= 1
        ):
            return mean, 0.0

        mcse = float(
            np.std(
                values,
                ddof=1,
            )
            / np.sqrt(
                len(values)
            )
        )

        return mean, mcse

    @staticmethod
    def _wilson_interval(
        successes,
        n,
        z=1.96,
    ):

        if n == 0:
            return (
                np.nan,
                np.nan,
            )

        phat = (
            successes
            / n
        )

        z2 = (
            z ** 2
        )

        denominator = (
            1.0
            + z2 / n
        )

        center = (
            phat
            + z2
            / (2.0 * n)
        ) / denominator

        half = (
            z
            * np.sqrt(
                phat
                * (1.0 - phat)
                / n
                + z2
                / (
                    4.0
                    * n ** 2
                )
            )
            / denominator
        )

        return (
            max(
                0.0,
                center - half,
            ),
            min(
                1.0,
                center + half,
            ),
        )

    # ------------------------------------------------------------------
    # STOCHASTIC KERNEL
    # ------------------------------------------------------------------

    def simulate_condition(
        self,
        p,
        tau,
        fn_rate,
    ):
        """
        Simulate one parameter condition.

        For susceptible target cell j:

            q_j = 1 - (1 - p)^k_j

        where k_j is the number of actively compromised
        source cells with a directed executable-authority
        interface to target j.

        Propagation denotes the extension of an adverse
        executable condition across purpose-bound domains
        of delegated authority.

        It does not necessarily denote malware transmission
        or technical intrusion.
        """

        if not (
            0.0
            <= p
            <= 1.0
        ):
            raise ValueError(
                "p must lie in [0,1]."
            )

        if tau < 0:
            raise ValueError(
                "tau must be "
                "non-negative."
            )

        if not (
            0.0
            <= fn_rate
            <= 1.0
        ):
            raise ValueError(
                "fn_rate must lie "
                "in [0,1]."
            )

        R = (
            self.num_replicates
        )

        N = (
            self.num_cells
        )

        H = (
            self.sweep_horizon
        )

        # IMPORTANT:
        # Preserve the experimental random-number structure.
        # The generator is reinitialized with the same seed
        # for every topology-condition.
        rng = (
            np.random.default_rng(
                self.seed
            )
        )

        compromised = (
            np.zeros(
                (R, N),
                dtype=bool,
            )
        )

        # Cell 0 is the originating compromised cell.
        compromised[
            :,
            0,
        ] = True

        # Large value represents no isolation
        # during the observation horizon.
        isolation_at = (
            np.full(
                (R, N),
                H
                + max(
                    TAU_VALUES
                )
                + 2,
                dtype=int,
            )
        )

        # Detection of originating compromise.
        initial_detection_u = (
            rng.random(
                R
            )
        )

        initial_detected = (
            initial_detection_u
            >= fn_rate
        )

        isolation_at[
            initial_detected,
            0,
        ] = tau

        healthy_secondary_cell_steps = (
            np.zeros(
                R,
                dtype=float,
            )
        )

        active_compromise_cell_steps = (
            np.zeros(
                R,
                dtype=float,
            )
        )

        for t in range(H):

            active_compromised = (
                compromised
                & (
                    t
                    < isolation_at
                )
            )

            healthy_secondary = (
                ~compromised[
                    :,
                    1:
                ]
            )

            healthy_secondary_cell_steps += (
                healthy_secondary.sum(
                    axis=1
                )
            )

            active_compromise_cell_steps += (
                active_compromised.sum(
                    axis=1
                )
            )

            # ------------------------------------------------------
            # TOPOLOGY-AWARE PROPAGATION
            #
            # active_source_counts[r, j]
            # is the number of active compromised source
            # cells i for which A[i,j] = 1.
            #
            # For S0 and a susceptible target j this is
            # exactly the active-source count in the
            # original maximal-connectivity model.
            # ------------------------------------------------------

            active_source_counts = (
                active_compromised
                .astype(
                    np.int64
                )
                @ self.adjacency
            )

            propagation_probability = (
                1.0
                - np.power(
                    1.0 - p,
                    active_source_counts,
                )
            )

            # Preserve experimental draw shape and order.
            propagation_u = (
                rng.random(
                    (R, N)
                )
            )

            susceptible = (
                ~compromised
            )

            newly_compromised = (
                susceptible
                & (
                    propagation_u
                    < propagation_probability
                )
            )

            # Origin is already compromised.
            newly_compromised[
                :,
                0,
            ] = False

            compromised |= (
                newly_compromised
            )

            # Preserve experimental draw shape and order.
            detection_u = (
                rng.random(
                    (R, N)
                )
            )

            newly_detected = (
                newly_compromised
                & (
                    detection_u
                    >= fn_rate
                )
            )

            # A cell compromised during step t
            # first becomes active at t+1.
            #
            # tau = 0 therefore isolates a detected
            # newly compromised cell before its first
            # propagation opportunity.
            isolation_at[
                newly_detected
            ] = (
                t
                + 1
                + tau
            )

        # ----------------------------------------------------------
        # END-OF-HORIZON OUTCOMES
        # ----------------------------------------------------------

        secondary_compromised = (
            compromised[
                :,
                1:
            ]
            .sum(
                axis=1
            )
        )

        systemic_event = (
            secondary_compromised
            >= (
                self
                .systemic_secondary_threshold
            )
        )

        systemic_successes = int(
            systemic_event.sum()
        )

        contagion_rate = (
            100.0
            * systemic_successes
            / R
        )

        (
            contagion_low,
            contagion_high,
        ) = (
            self._wilson_interval(
                systemic_successes,
                R,
            )
        )

        contagion_low *= (
            100.0
        )

        contagion_high *= (
            100.0
        )

        strategic_velocity_runs = (
            100.0
            * healthy_secondary_cell_steps
            / (
                (N - 1)
                * H
            )
        )

        (
            strategic_velocity_mean,
            strategic_velocity_mcse,
        ) = (
            self._mean_mcse(
                strategic_velocity_runs
            )
        )

        propagated_exposure_runs = (
            secondary_compromised
            .astype(
                float
            )
        )

        (
            pe_mean,
            pe_mcse,
        ) = (
            self._mean_mcse(
                propagated_exposure_runs
            )
        )

        cep_runs = (
            active_compromise_cell_steps
        )

        (
            cep_mean,
            cep_mcse,
        ) = (
            self._mean_mcse(
                cep_runs
            )
        )

        leakage_rate = (
            100.0
            * np.mean(
                secondary_compromised
                > 0
            )
        )

        # IMPORTANT:
        # Return schema and order are preserved from
        # the experiment-time canonical output so that
        # S0 can be regression-tested exactly.

        return {
            "p": float(p),
            "tau": int(tau),
            "fn_rate": float(
                fn_rate
            ),
            "replicates": int(R),

            "systemic_contagion_pct": (
                contagion_rate
            ),

            "systemic_contagion_ci_low": (
                contagion_low
            ),

            "systemic_contagion_ci_high": (
                contagion_high
            ),

            "cross_cell_leakage_pct": float(
                leakage_rate
            ),

            "strategic_velocity_pct": (
                strategic_velocity_mean
            ),

            "strategic_velocity_mcse": (
                strategic_velocity_mcse
            ),

            "propagated_exposure": (
                pe_mean
            ),

            "propagated_exposure_mcse": (
                pe_mcse
            ),

            "compromised_execution_persistence": (
                cep_mean
            ),

            "compromised_execution_persistence_mcse": (
                cep_mcse
            ),

            "mean_secondary_cells_affected": float(
                np.mean(
                    secondary_compromised
                )
            ),
        }

    # ------------------------------------------------------------------
    # 196-CONDITION SWEEP
    # ------------------------------------------------------------------

    def run_parameter_sweep(
        self,
    ):

        rows = []

        condition = 0

        for p in P_VALUES:
            for tau in TAU_VALUES:
                for fn_rate in FN_VALUES:

                    condition += 1

                    result = (
                        self.simulate_condition(
                            p=p,
                            tau=tau,
                            fn_rate=fn_rate,
                        )
                    )

                    result[
                        "condition_id"
                    ] = condition

                    rows.append(
                        result
                    )

        df = pd.DataFrame(
            rows
        )

        if (
            len(df)
            != 196
        ):
            raise RuntimeError(
                "Expected 196 conditions; "
                f"obtained {len(df)}."
            )

        return df


# ======================================================================
# COMPUTATIONAL VERIFICATION
# ======================================================================

def run_verification_checks(
    replicates,
    seed,
    horizon,
):

    test_replicates = max(
        200,
        min(
            replicates,
            1000,
        ),
    )

    # --------------------------------------------------------------
    # Test 1:
    # p = 0 prevents secondary propagation.
    # --------------------------------------------------------------

    s0 = (
        InstitutionalContainmentStressTest(
            scenario_id=(
                "S0_maximal_connectivity"
            ),
            num_replicates=(
                test_replicates
            ),
            sweep_horizon=horizon,
            seed=seed,
        )
    )

    zero_propagation = (
        s0.simulate_condition(
            p=0.0,
            tau=6,
            fn_rate=1.0,
        )
    )

    assert np.isclose(
        zero_propagation[
            "systemic_contagion_pct"
        ],
        0.0,
    )

    assert np.isclose(
        zero_propagation[
            "propagated_exposure"
        ],
        0.0,
    )

    # --------------------------------------------------------------
    # Test 2:
    # Immediate perfect mediation prevents propagation.
    # --------------------------------------------------------------

    perfect_mediation = (
        s0.simulate_condition(
            p=1.0,
            tau=0,
            fn_rate=0.0,
        )
    )

    assert np.isclose(
        perfect_mediation[
            "systemic_contagion_pct"
        ],
        0.0,
    )

    assert np.isclose(
        perfect_mediation[
            "compromised_execution_persistence"
        ],
        0.0,
    )

    assert np.isclose(
        perfect_mediation[
            "strategic_velocity_pct"
        ],
        100.0,
    )

    # --------------------------------------------------------------
    # Test 3:
    # Certain propagation with complete non-detection
    # reaches all four secondary cells under S0.
    # --------------------------------------------------------------

    uncontrolled = (
        s0.simulate_condition(
            p=1.0,
            tau=6,
            fn_rate=1.0,
        )
    )

    assert np.isclose(
        uncontrolled[
            "systemic_contagion_pct"
        ],
        100.0,
    )

    assert np.isclose(
        uncontrolled[
            "propagated_exposure"
        ],
        NUM_CELLS - 1,
    )

    # --------------------------------------------------------------
    # Test 4:
    # Newly compromised cells do not propagate
    # during the same simulation step.
    # --------------------------------------------------------------

    s1_one_step = (
        InstitutionalContainmentStressTest(
            scenario_id=(
                "S1_sparse_sequential"
            ),
            num_replicates=(
                test_replicates
            ),
            sweep_horizon=1,
            seed=seed,
        )
    )

    no_same_step_cascade = (
        s1_one_step.simulate_condition(
            p=1.0,
            tau=6,
            fn_rate=1.0,
        )
    )

    assert np.isclose(
        no_same_step_cascade[
            "propagated_exposure"
        ],
        1.0,
    )

    assert np.isclose(
        no_same_step_cascade[
            "systemic_contagion_pct"
        ],
        0.0,
    )

    print(
        "[PASS] Computational "
        "verification checks."
    )


# ======================================================================
# S0 EXACT REGRESSION
# ======================================================================

def compare_s0_exact(
    generated_df,
    reference_path,
):

    reference_path = Path(
        reference_path
    )

    if not (
        reference_path.exists()
    ):
        raise FileNotFoundError(
            "S0 regression reference "
            "not found: "
            f"{reference_path}"
        )

    reference_df = pd.read_csv(
        reference_path
    )

    generated_df = (
        generated_df
        .sort_values(
            "condition_id"
        )
        .reset_index(
            drop=True
        )
    )

    reference_df = (
        reference_df
        .sort_values(
            "condition_id"
        )
        .reset_index(
            drop=True
        )
    )

    if (
        list(
            reference_df.columns
        )
        != list(
            generated_df.columns
        )
    ):
        raise RuntimeError(
            "S0 regression failed: "
            "column schemas differ.\n\n"
            f"Reference:\n"
            f"{list(reference_df.columns)}\n\n"
            f"Generated:\n"
            f"{list(generated_df.columns)}"
        )

    if (
        len(reference_df)
        != len(generated_df)
    ):
        raise RuntimeError(
            "S0 regression failed: "
            "row counts differ."
        )

    report_rows = []

    all_exact = True

    for column in (
        reference_df.columns
    ):

        ref_values = (
            reference_df[
                column
            ]
            .to_numpy()
        )

        new_values = (
            generated_df[
                column
            ]
            .to_numpy()
        )

        exact = (
            np.array_equal(
                ref_values,
                new_values,
            )
        )

        if (
            pd.api.types
            .is_numeric_dtype(
                reference_df[
                    column
                ]
            )
            and
            pd.api.types
            .is_numeric_dtype(
                generated_df[
                    column
                ]
            )
        ):

            diff = np.abs(
                ref_values.astype(
                    float
                )
                - new_values.astype(
                    float
                )
            )

            max_abs_diff = float(
                np.max(
                    diff
                )
            )

        else:

            max_abs_diff = (
                0.0
                if exact
                else np.nan
            )

        report_rows.append(
            {
                "column": column,
                "exact_match": (
                    bool(exact)
                ),
                "max_abs_diff": (
                    max_abs_diff
                ),
            }
        )

        if not exact:
            all_exact = False

    return (
        all_exact,
        pd.DataFrame(
            report_rows
        ),
    )


# ======================================================================
# SCENARIO OUTPUT HELPERS
# ======================================================================

def add_scenario_metadata(
    df,
    scenario_id,
):

    metadata = (
        topology_metadata(
            scenario_id
        )
    )

    enriched = (
        df.copy()
    )

    # Add bounded-leakage gap as a derived
    # scenario-analysis quantity.
    enriched[
        "bounded_leakage_gap_pp"
    ] = (
        enriched[
            "cross_cell_leakage_pct"
        ]
        - enriched[
            "systemic_contagion_pct"
        ]
    )

    for key in reversed(
        list(
            metadata.keys()
        )
    ):

        enriched.insert(
            0,
            key,
            metadata[key],
        )

    return enriched


def verify_s0_s2_matched_leakage(
    combined_df,
):

    keys = [
        "p",
        "tau",
        "fn_rate",
    ]

    s0 = (
        combined_df[
            combined_df[
                "scenario_id"
            ]
            == (
                "S0_maximal_connectivity"
            )
        ][
            keys
            + [
                "cross_cell_leakage_pct"
            ]
        ]
        .sort_values(
            keys
        )
        .reset_index(
            drop=True
        )
    )

    s2 = (
        combined_df[
            combined_df[
                "scenario_id"
            ]
            == "S2_hub_mediated"
        ][
            keys
            + [
                "cross_cell_leakage_pct"
            ]
        ]
        .sort_values(
            keys
        )
        .reset_index(
            drop=True
        )
    )

    if (
        len(s0) != 196
        or len(s2) != 196
    ):
        raise RuntimeError(
            "S0-S2 matched comparison "
            "does not contain 196 "
            "conditions per topology."
        )

    if not np.array_equal(
        s0[
            "cross_cell_leakage_pct"
        ].to_numpy(),
        s2[
            "cross_cell_leakage_pct"
        ].to_numpy(),
    ):
        raise RuntimeError(
            "S0-S2 matched leakage "
            "verification failed."
        )

    print(
        "[PASS] S0 and S2 cross-cell "
        "leakage are identical across "
        "all 196 matched conditions."
    )


def verify_manuscript_topology_ordering(
    combined_df,
):

    keys = [
        "p",
        "tau",
        "fn_rate",
    ]

    s0 = (
        combined_df[
            combined_df[
                "scenario_id"
            ]
            == (
                "S0_maximal_connectivity"
            )
        ]
        .sort_values(
            keys
        )
        .reset_index(
            drop=True
        )
    )

    s2 = (
        combined_df[
            combined_df[
                "scenario_id"
            ]
            == "S2_hub_mediated"
        ]
        .sort_values(
            keys
        )
        .reset_index(
            drop=True
        )
    )

    if not np.all(
        s2[
            "systemic_contagion_pct"
        ].to_numpy()
        <=
        s0[
            "systemic_contagion_pct"
        ].to_numpy()
    ):
        raise RuntimeError(
            "S2 systemic contagion "
            "exceeds S0 in at least "
            "one matched condition."
        )

    if not np.all(
        s2[
            "propagated_exposure"
        ].to_numpy()
        <=
        s0[
            "propagated_exposure"
        ].to_numpy()
    ):
        raise RuntimeError(
            "S2 propagated exposure "
            "exceeds S0 in at least "
            "one matched condition."
        )

    if not np.all(
        s2[
            "strategic_velocity_pct"
        ].to_numpy()
        >=
        s0[
            "strategic_velocity_pct"
        ].to_numpy()
    ):
        raise RuntimeError(
            "S2 strategic velocity "
            "falls below S0 in at "
            "least one matched "
            "condition."
        )

    print(
        "[PASS] S0-S2 matched "
        "topology ordering checks."
    )


def scenario_summary(
    combined_df,
):

    outcomes = (
        "systemic_contagion_pct",
        "cross_cell_leakage_pct",
        "strategic_velocity_pct",
        "propagated_exposure",
        "compromised_execution_persistence",
        "bounded_leakage_gap_pp",
    )

    rows = []

    for scenario_id in (
        SCENARIO_ORDER
    ):

        part = (
            combined_df[
                combined_df[
                    "scenario_id"
                ]
                == scenario_id
            ]
        )

        if (
            len(part)
            != 196
        ):
            raise RuntimeError(
                f"{scenario_id}: "
                "expected 196 rows; "
                f"obtained {len(part)}."
            )

        row = (
            topology_metadata(
                scenario_id
            )
        )

        for outcome in outcomes:

            row[
                f"design_mean_{outcome}"
            ] = float(
                part[
                    outcome
                ].mean()
            )

        anchor = (
            part[
                np.isclose(
                    part["p"],
                    0.010,
                )
                & (
                    part["tau"]
                    == 5
                )
                & np.isclose(
                    part[
                        "fn_rate"
                    ],
                    0.20,
                )
            ]
        )

        if (
            len(anchor)
            != 1
        ):
            raise RuntimeError(
                f"{scenario_id}: "
                "anchor condition "
                "is not unique."
            )

        anchor_row = (
            anchor.iloc[0]
        )

        for outcome in outcomes:

            row[
                f"anchor_{outcome}"
            ] = float(
                anchor_row[
                    outcome
                ]
            )

        row[
            "anchor_systemic_ci_low"
        ] = float(
            anchor_row[
                "systemic_contagion_ci_low"
            ]
        )

        row[
            "anchor_systemic_ci_high"
        ] = float(
            anchor_row[
                "systemic_contagion_ci_high"
            ]
        )

        rows.append(
            row
        )

    return pd.DataFrame(
        rows
    )


# ======================================================================
# MANIFEST
# ======================================================================

def write_manifest(
    path,
    args,
):

    scenarios = {}

    for scenario_id in (
        SCENARIO_ORDER
    ):

        spec = TOPOLOGIES[
            scenario_id
        ]

        adjacency = (
            build_adjacency_matrix(
                spec
            )
        )

        metadata = (
            topology_metadata(
                scenario_id
            )
        )

        scenarios[
            scenario_id
        ] = {
            **metadata,

            "interpretation": (
                spec[
                    "interpretation"
                ]
            ),

            "cell_labels": list(
                spec[
                    "cell_labels"
                ]
            ),

            "edges_one_based": [
                [
                    int(i + 1),
                    int(j + 1),
                ]
                for i, j
                in spec["edges"]
            ],

            "adjacency_matrix": (
                adjacency.tolist()
            ),
        }

    manifest = {

        "study_title": (
            "Governing Agentic AI Under "
            "Deep Uncertainty: "
            "Scenario-Based Stress Tests "
            "of Institutional Containment"
        ),

        "model_type": (
            "scenario-based structured "
            "stochastic design experiment"
        ),

        "interpretive_status": (
            "theory-grounded synthetic "
            "stress test; not calibrated "
            "to empirical frequencies of "
            "real-world agentic-AI incidents"
        ),

        "reproducibility_gate": (
            "S0 maximal-connectivity output "
            "must exactly match the verified "
            "196-condition reference sweep "
            "before S1-S3 are executed"
        ),

        "seed": (
            args.seed
        ),

        "replicates_per_condition": (
            args.replicates
        ),

        "num_cells": (
            NUM_CELLS
        ),

        "sweep_horizon_steps": (
            args.horizon
        ),

        "conditions_per_topology": (
            196
        ),

        "total_parameter_conditions": (
            784
        ),

        "total_containment_episodes": (
            784
            * args.replicates
        ),

        "parameters": {
            "p": list(
                P_VALUES
            ),
            "tau": list(
                TAU_VALUES
            ),
            "fn_rate": list(
                FN_VALUES
            ),
        },

        "parameter_interpretation": {

            "p": (
                "per-active-source, "
                "per-susceptible-cell, "
                "per-step propagation "
                "stress probability"
            ),

            "tau": (
                "relative mediation delay "
                "in abstract simulation steps; "
                "not calibrated to clock time"
            ),

            "fn_rate": (
                "episode-level probability "
                "that a compromised cell "
                "remains undetected during "
                "the modeled episode"
            ),
        },

        "timing_rules": {

            "new_compromise": (
                "a cell compromised during "
                "step t first becomes active "
                "at step t+1"
            ),

            "tau_zero": (
                "a detected cell with tau=0 "
                "is isolated before its first "
                "or next propagation opportunity"
            ),

            "same_step_cascading": False,

            "endogenous_recovery": False,
        },

        "outcome_definitions": {

            "cross_cell_leakage": (
                "at least one secondary "
                "governance cell is ever "
                "compromised"
            ),

            "systemic_contagion": (
                "at least two secondary "
                "governance cells are ever "
                "compromised"
            ),

            "strategic_velocity": (
                "share of secondary cell-time "
                "remaining uncompromised"
            ),

            "propagated_exposure": (
                "number of secondary governance "
                "cells reached"
            ),

            "compromised_execution_persistence": (
                "cumulative active compromised "
                "cell-steps"
            ),

            "bounded_leakage_gap": (
                "cross-cell leakage percentage "
                "minus systemic-contagion "
                "percentage"
            ),
        },

        "scenarios": scenarios,

        "excluded_claims": [
            (
                "empirical prediction of "
                "real-world incident frequencies"
            ),
            (
                "universal superiority of any "
                "governance topology"
            ),
            (
                "numerical measurement of the "
                "normative magnitude of value "
                "missing or value slippage"
            ),
        ],
    }

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            manifest,
            file,
            indent=2,
        )


# ======================================================================
# OUTPUT DIRECTORY
# ======================================================================

def prepare_output_directory(
    output_dir,
    overwrite,
):
    output_dir = Path(
        output_dir
    )

    if output_dir.exists():

        if not output_dir.is_dir():
            raise RuntimeError(
                "Output path exists but is not "
                "a directory:\n"
                f"{output_dir}"
            )

        if any(output_dir.iterdir()):

            if not overwrite:
                raise RuntimeError(
                    "Output directory is not empty:\n"
                    f"{output_dir}\n\n"
                    "Use --overwrite or specify "
                    "another output directory."
                )

            # Do not delete the directory itself.
            # This avoids permission problems in
            # Dropbox/WSL environments.
            print(
                "[INFO] Existing output directory "
                "will be overwritten in place:"
            )
            print(
                f"       {output_dir}"
            )

    else:
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    return output_dir


# ======================================================================
# MAIN EXPERIMENT
# ======================================================================

def main():

    parser = (
        argparse.ArgumentParser(
            description=(
                "Scenario-based stochastic "
                "stress test of institutional "
                "containment."
            )
        )
    )

    parser.add_argument(
        "--replicates",
        type=int,
        default=1000,
        help=(
            "Monte Carlo replications per "
            "topology-condition "
            "(default: 1000)."
        ),
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help=(
            "Random seed "
            "(default: 42)."
        ),
    )

    parser.add_argument(
        "--horizon",
        type=int,
        default=12,
        help=(
            "Observation horizon in "
            "simulation steps "
            "(default: 12)."
        ),
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help=(
            "Run only the S0 exact "
            "regression gate."
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Replace an existing "
            "output directory."
        ),
    )

    parser.add_argument(
        "--reference",
        type=str,
        default="./validation/s0_reference_196.csv",
        help="Verified S0 regression reference sweep.",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./simulation_output",
        help="Output directory.",
    )

    args = (
        parser.parse_args()
    )

    validate_topologies()

    run_verification_checks(
        replicates=(
            args.replicates
        ),
        seed=args.seed,
        horizon=args.horizon,
    )

    output_dir = (
        prepare_output_directory(
            args.output_dir,
            args.overwrite,
        )
    )

    print()
    print("=" * 72)
    print(
        "INSTITUTIONAL CONTAINMENT "
        "STRESS TEST"
    )
    print("=" * 72)

    # ==============================================================
    # STEP 1: S0 EXACT REGRESSION
    # ==============================================================

    print()
    print(
        "STEP 1: S0 EXACT REGRESSION"
    )
    print("-" * 72)

    s0_simulator = (
        InstitutionalContainmentStressTest(
            scenario_id=(
                "S0_maximal_connectivity"
            ),
            num_replicates=(
                args.replicates
            ),
            sweep_horizon=(
                args.horizon
            ),
            seed=args.seed,
        )
    )

    s0_df = (
        s0_simulator
        .run_parameter_sweep()
    )

    (
        exact,
        regression_report,
    ) = (
        compare_s0_exact(
            generated_df=s0_df,
            reference_path=(
                args.reference
            ),
        )
    )

    regression_report.to_csv(
        output_dir
        / "s0_regression_check.csv",
        index=False,
    )

    if not exact:

        failed = (
            regression_report[
                ~regression_report[
                    "exact_match"
                ]
            ]
        )

        print()
        print(
            "S0 REGRESSION FAILED"
        )

        print(
            failed.to_string(
                index=False
            )
        )

        raise RuntimeError(
            "S0 does not exactly reproduce "
            "the verified 196-condition "
            "reference sweep. "
            "S1-S3 were not run."
        )

    print(
        "[PASS] S0 exactly matches "
        "the verified 196-condition "
        "reference sweep."
    )

    s0_dir = (
        output_dir
        / "S0_maximal_connectivity"
    )

    s0_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    s0_df.to_csv(
        s0_dir
        / "parameter_sweep_196.csv",
        index=False,
    )

    if args.validate_only:

        write_manifest(
            output_dir
            / "topology_manifest.json",
            args,
        )

        print()
        print(
            "S0 validation completed."
        )

        return

    # ==============================================================
    # STEP 2: S1-S3
    # ==============================================================

    all_frames = [
        add_scenario_metadata(
            s0_df,
            "S0_maximal_connectivity",
        )
    ]

    for scenario_id in (
        SCENARIO_ORDER[1:]
    ):

        print()
        print(
            f"RUNNING {scenario_id}"
        )

        print("-" * 72)

        simulator = (
            InstitutionalContainmentStressTest(
                scenario_id=(
                    scenario_id
                ),
                num_replicates=(
                    args.replicates
                ),
                sweep_horizon=(
                    args.horizon
                ),
                seed=args.seed,
            )
        )

        scenario_df = (
            simulator
            .run_parameter_sweep()
        )

        scenario_dir = (
            output_dir
            / scenario_id
        )

        scenario_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        scenario_df.to_csv(
            scenario_dir
            / "parameter_sweep_196.csv",
            index=False,
        )

        all_frames.append(
            add_scenario_metadata(
                scenario_df,
                scenario_id,
            )
        )

    # ==============================================================
    # STEP 3: COMBINED OUTPUT
    # ==============================================================

    combined_df = (
        pd.concat(
            all_frames,
            ignore_index=True,
        )
    )

    if (
        len(combined_df)
        != 784
    ):
        raise RuntimeError(
            "Expected 784 combined "
            "topology-condition rows; "
            f"obtained {len(combined_df)}."
        )

    verify_s0_s2_matched_leakage(
        combined_df
    )

    verify_manuscript_topology_ordering(
        combined_df
    )

    combined_path = (
        output_dir
        / "scenario_sweep_784.csv"
    )

    combined_df.to_csv(
        combined_path,
        index=False,
    )

    summary_df = (
        scenario_summary(
            combined_df
        )
    )

    summary_path = (
        output_dir
        / "scenario_summary.csv"
    )

    summary_df.to_csv(
        summary_path,
        index=False,
    )

    write_manifest(
        output_dir
        / "topology_manifest.json",
        args,
    )

    # ==============================================================
    # REPORT
    # ==============================================================

    print()
    print("=" * 72)
    print(
        "STRESS TEST COMPLETED"
    )
    print("=" * 72)

    print(
        "[PASS] S0 exact regression."
    )

    print(
        "[PASS] S1 Sparse Sequential "
        "Topology."
    )

    print(
        "[PASS] S2 Hub-Mediated "
        "Topology."
    )

    print(
        "[PASS] S3 Layered Topology."
    )

    print(
        "[PASS] 784 topology-condition "
        "rows generated."
    )

    print(
        f"Total containment episodes: "
        f"{784 * args.replicates:,}"
    )

    print()
    print(
        f"Combined sweep : "
        f"{combined_path}"
    )

    print(
        f"Summary        : "
        f"{summary_path}"
    )

    print(
        f"Manifest       : "
        f"{output_dir / 'topology_manifest.json'}"
    )

    print(
        f"Regression     : "
        f"{output_dir / 's0_regression_check.csv'}"
    )

    print()
    print(
        "DESIGN-WIDE SUMMARY"
    )

    print("-" * 72)

    display_columns = [
        "scenario_id",
        (
            "design_mean_"
            "systemic_contagion_pct"
        ),
        (
            "design_mean_"
            "cross_cell_leakage_pct"
        ),
        (
            "design_mean_"
            "propagated_exposure"
        ),
        (
            "design_mean_"
            "strategic_velocity_pct"
        ),
        (
            "design_mean_"
            "compromised_execution_persistence"
        ),
        (
            "design_mean_"
            "bounded_leakage_gap_pp"
        ),
    ]

    print(
        summary_df[
            display_columns
        ].to_string(
            index=False
        )
    )

    print("=" * 72)


if __name__ == "__main__":
    main()
    
