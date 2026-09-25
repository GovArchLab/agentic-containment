"""
mge_simulation_full_robustness.py

Revised robustness engine for:
Regulating the Unknowns of Agentic AI:
Institutional Containment and Runtime Mediation
of Value Missing and Value Slippage

Purpose
-------
1. Preserve the original fixed-scenario outputs as legacy deterministic anchors.
2. Add a genuine stochastic parameter sweep over:
       p   in {0.001, 0.005, 0.010, 0.020}
       tau in {0, 1, 2, 3, 4, 5, 6}
       FN  in {0, .05, .10, .15, .20, .25, .30}
3. Run 1,000 Monte Carlo replications per condition by default.
4. Treat simulation as a structured design experiment rather than
   an estimator of real-world failure frequencies.
5. Keep Action Trace as the primary audit representation.

The sweep contains 4 * 7 * 7 = 196 parameter conditions.
"""

import argparse
import datetime
import hashlib
import json
import os

import numpy as np
import pandas as pd


class ModelGovernanceEngineSimulator:

    P_VALUES = (0.001, 0.005, 0.010, 0.020)
    TAU_VALUES = (0, 1, 2, 3, 4, 5, 6)
    FN_VALUES = (0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30)

    def __init__(
        self,
        intervals=10000,
        num_cells=5,
        exploit_interval=2604,
        num_replicates=1000,
        sweep_horizon=12,
        systemic_secondary_threshold=2,   # v2: from 1 
        seed=42,
        output_dir="./simulation_output",
    ):
        if num_cells < 2:
            raise ValueError("num_cells must be at least 2.")

        if num_replicates < 1:
            raise ValueError("num_replicates must be positive.")

        if sweep_horizon < 1:
            raise ValueError("sweep_horizon must be positive.")

        if systemic_secondary_threshold < 1:
            raise ValueError(
                "systemic_secondary_threshold must be at least 1."
            )

        if systemic_secondary_threshold > num_cells - 1:
            raise ValueError(
                "systemic_secondary_threshold cannot exceed "
                "the number of secondary cells."
            )

        self.intervals = intervals
        self.num_cells = num_cells
        self.exploit_interval = exploit_interval
        self.num_replicates = num_replicates
        self.sweep_horizon = sweep_horizon
        self.systemic_secondary_threshold = (
            systemic_secondary_threshold
        )
        self.seed = seed

        self.output_dir = output_dir
        self.registry_dir = os.path.join(
            output_dir,
            "forensic_registry",
        )

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.registry_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # LEGACY FIXED-SCENARIO ANCHOR
    # ------------------------------------------------------------------

    def legacy_fixed_scenarios(self):
        """
        Preserve the numerical outputs in the rejected manuscript code.

        IMPORTANT:
        These values are deterministic illustrative anchors.
        They are not produced by the stochastic robustness engine and
        should not be described as Monte Carlo estimates.
        """

        rows = [
            {
                "architecture": "Monolithic baseline",
                "scenario": "Legacy baseline",
                "p": np.nan,
                "tau": np.nan,
                "fn_rate": np.nan,
                "systemic_contagion_pct": 73.96,
                "strategic_velocity_pct": 0.00,
                "accumulated_value_missing_usd": 12468750.00,
                "value_slippage_usd": 8500.00,
                "status": "legacy deterministic anchor",
            },
            {
                "architecture": "Purpose-bound governance cells",
                "scenario": "Ideal Control",
                "p": 0.001,
                "tau": 0,
                "fn_rate": 0.00,
                "systemic_contagion_pct": 0.00,
                "strategic_velocity_pct": 45.14,
                "accumulated_value_missing_usd": 11767500.00,
                "value_slippage_usd": 8500.00,
                "status": "legacy deterministic anchor",
            },
            {
                "architecture": "Purpose-bound governance cells",
                "scenario": "Standard Lag",
                "p": 0.001,
                "tau": 2,
                "fn_rate": 0.05,
                "systemic_contagion_pct": 0.00,
                "strategic_velocity_pct": 45.14,
                "accumulated_value_missing_usd": 11767500.00,
                "value_slippage_usd": 12500.00,
                "status": "legacy deterministic anchor",
            },
            {
                "architecture": "Purpose-bound governance cells",
                "scenario": "High Volatility",
                "p": 0.010,
                "tau": 1,
                "fn_rate": 0.10,
                "systemic_contagion_pct": 0.00,
                "strategic_velocity_pct": 45.14,
                "accumulated_value_missing_usd": 11767500.00,
                "value_slippage_usd": 18500.00,
                "status": "legacy deterministic anchor",
            },
            {
                "architecture": "Purpose-bound governance cells",
                "scenario": "Adversarial Stress",
                "p": 0.010,
                "tau": 5,
                "fn_rate": 0.20,
                "systemic_contagion_pct": 25.00,
                "strategic_velocity_pct": 26.32,
                "accumulated_value_missing_usd": 11767500.00,
                "value_slippage_usd": 42500.00,
                "status": "legacy deterministic anchor",
            },
        ]

        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # CONFIDENCE INTERVALS
    # ------------------------------------------------------------------

    @staticmethod
    def _mean_mcse(values):
        values = np.asarray(values, dtype=float)

        mean = float(np.mean(values))

        if len(values) <= 1:
            return mean, 0.0

        mcse = float(
            np.std(values, ddof=1) /
            np.sqrt(len(values))
        )

        return mean, mcse    


    @staticmethod
    def _wilson_interval(successes, n, z=1.96):
        if n == 0:
            return np.nan, np.nan

        phat = successes / n
        z2 = z ** 2

        denominator = 1.0 + z2 / n

        center = (
            phat + z2 / (2.0 * n)
        ) / denominator

        half = (
            z
            * np.sqrt(
                phat * (1.0 - phat) / n
                + z2 / (4.0 * n ** 2)
            )
            / denominator
        )

        return (
            max(0.0, center - half),
            min(1.0, center + half),
        )

    # ------------------------------------------------------------------
    # STOCHASTIC CONTAINMENT MODEL
    # ------------------------------------------------------------------

    def simulate_condition(
        self,
        p,
        tau,
        fn_rate,
    ):
        """
        Simulate one parameter condition.

        Interpretation
        --------------
        p:
            Per-active-source, per-susceptible-cell, per-step probability
            of cross-cell propagation.

        tau:
            Number of simulation steps between successful detection and
            isolation of the compromised cell.

        fn_rate:
            Episode-level probability that a compromised cell, including
            the originating cell at initialization, escapes detection
            during the modeled containment episode.

        Dynamics
        --------
        One governance cell begins compromised.

        Detected compromised cells are scheduled for isolation after tau
        steps.

        Undetected compromised cells remain active through the observation
        window.

        Each active compromised cell can expose every still-susceptible
        cell to cross-cell propagation probability p.

        The model intentionally holds N, network structure, and the
        propagation function fixed.
        """

        if not 0.0 <= p <= 1.0:
            raise ValueError("p must lie in [0, 1].")

        if tau < 0:
            raise ValueError("tau must be non-negative.")

        if not 0.0 <= fn_rate <= 1.0:
            raise ValueError("fn_rate must lie in [0, 1].")

        R = self.num_replicates
        N = self.num_cells
        H = self.sweep_horizon

        # Reinitialize with the same seed for every parameter cell.
        # This creates common random numbers across conditions and reduces
        # irrelevant Monte Carlo noise in comparative response surfaces.
        rng = np.random.default_rng(self.seed)

        compromised = np.zeros(
            (R, N),
            dtype=bool,
        )

        # Cell 0 is the originating compromised governance cell.
        compromised[:, 0] = True

        # Large value represents "not isolated during observation window."
        isolation_at = np.full(
            (R, N),
            H + max(self.TAU_VALUES) + 2,
            dtype=int,
        )

        # Detection of the originating incident.
        initial_detection_u = rng.random(R)

        initial_detected = (
            initial_detection_u >= fn_rate
        )

        isolation_at[
            initial_detected,
            0
        ] = tau

        healthy_secondary_cell_steps = np.zeros(
            R,
            dtype=float,
        )

        active_compromise_cell_steps = np.zeros(
            R,
            dtype=float,
        )

        for t in range(H):

            # A compromised cell remains propagation-capable until the
            # scheduled mediation time.
            active_compromised = (
                compromised
                & (t < isolation_at)
            )

            # Strategic velocity is measured on cells other than the
            # originating incident cell.
            healthy_secondary = (
                ~compromised[:, 1:]
            )

            healthy_secondary_cell_steps += (
                healthy_secondary.sum(axis=1)
            )

            # Value-slippage proxy:
            # duration-intensity of execution divergence before mediation.
            active_compromise_cell_steps += (
                active_compromised.sum(axis=1)
            )

            active_sources = (
                active_compromised.sum(axis=1)
            )

            # If k active sources independently expose a susceptible cell
            # with probability p, the probability that at least one
            # exposure succeeds is:
            #
            #       q = 1 - (1-p)^k
            #
            propagation_probability = (
                1.0
                - np.power(
                    1.0 - p,
                    active_sources,
                )
            )

            propagation_u = rng.random(
                (R, N)
            )

            susceptible = ~compromised

            newly_compromised = (
                susceptible
                & (
                    propagation_u
                    < propagation_probability[:, None]
                )
            )

            # A cell newly compromised during step $t$ enters the active 
            # compromised state at step $t+1$, when it first contributes 
            # to compromised execution persistence and becomes eligible 
            # to generate propagation opportunities.
            newly_compromised[:, 0] = False

            compromised |= newly_compromised

            # Draw detection outcomes for every potential cell at every
            # step so the random-number stream is structurally identical
            # across parameter conditions.
            detection_u = rng.random(
                (R, N)
            )

            newly_detected = (
                newly_compromised
                & (detection_u >= fn_rate)
            )

            # A cell compromised during step t first becomes capable of
            # propagation at t+1.
            #
            # With tau = 0, successful detection therefore isolates the
            # newly compromised cell before its first propagation
            # opportunity.
            isolation_at[
                newly_detected
            ] = (
                t + 1 + tau
            )

        secondary_compromised = (
            compromised[:, 1:].sum(axis=1)
        )

        systemic_event = (
            secondary_compromised
            >= self.systemic_secondary_threshold
        )

        systemic_successes = int(
            systemic_event.sum()
        )

        contagion_rate = (
            100.0
            * systemic_successes
            / R
        )

        contagion_low, contagion_high = (
            self._wilson_interval(
                systemic_successes,
                R,
            )
        )

        contagion_low *= 100.0
        contagion_high *= 100.0

        # Strategic velocity:
        # proportion of secondary cell-capacity that remains unaffected
        # across the containment window.
        strategic_velocity_runs = (
            100.0
            * healthy_secondary_cell_steps
            / (
                (N - 1)
                * H
            )
        )

        strategic_velocity_mean, strategic_velocity_mcse = (
            self._mean_mcse(
                strategic_velocity_runs
            )
        )



        # Propagated Exposure (PE):
        # number of secondary governance cells reached by the
        # adverse executable condition.
        #
        # Unit:
        # secondary governance cells.
        propagated_exposure_runs = (
            secondary_compromised.astype(float)
        )

        pe_mean, pe_mcse = (
            self._mean_mcse(
                propagated_exposure_runs
            )
        )


        # Compromised Execution Persistence (CEP):
        # cumulative active compromised execution across cells
        # and simulation steps.
        #
        # Unit:
        # compromised cell-steps.
        cep_runs = (
            active_compromise_cell_steps
        )
        cep_mean, cep_mcse = (
            self._mean_mcse(
                cep_runs
            )
        )


        leakage_rate = (
            100.0
            * np.mean(
                secondary_compromised > 0
            )
        )

        return {
            "p": float(p),
            "tau": int(tau),
            "fn_rate": float(fn_rate),
            "replicates": int(R),

            "systemic_contagion_pct": contagion_rate,
            "systemic_contagion_ci_low": contagion_low,
            "systemic_contagion_ci_high": contagion_high,

            "cross_cell_leakage_pct": float(
                leakage_rate
            ),

            "strategic_velocity_pct": strategic_velocity_mean,
            "strategic_velocity_mcse": strategic_velocity_mcse,
            
            "propagated_exposure": pe_mean,
            "propagated_exposure_mcse": pe_mcse,

            "compromised_execution_persistence": cep_mean,
            "compromised_execution_persistence_mcse": cep_mcse,

#
#

            "mean_secondary_cells_affected": float(
                np.mean(secondary_compromised)
            ),
        }

    # ------------------------------------------------------------------
    # FULL 196-CONDITION SWEEP
    # ------------------------------------------------------------------

    def run_parameter_sweep(self):
        rows = []

        total = (
            len(self.P_VALUES)
            * len(self.TAU_VALUES)
            * len(self.FN_VALUES)
        )

        condition = 0

        for p in self.P_VALUES:
            for tau in self.TAU_VALUES:
                for fn_rate in self.FN_VALUES:

                    condition += 1

                    result = self.simulate_condition(
                        p=p,
                        tau=tau,
                        fn_rate=fn_rate,
                    )

                    result["condition_id"] = condition

                    rows.append(result)

        df = pd.DataFrame(rows)

        if len(df) != 196:
            raise RuntimeError(
                f"Expected 196 conditions; obtained {len(df)}."
            )

        print(
            f"Completed {len(df)} of {total} "
            "parameter conditions."
        )

        return df

    # ------------------------------------------------------------------
    # COMPUTATIONAL VERIFICATION
    # ------------------------------------------------------------------

    def run_verification_checks(self):
        """
        Boundary-condition tests for computational verification.

        These tests verify implementation logic.
        They do not constitute empirical validation.
        """

        original_R = self.num_replicates

        try:
            self.num_replicates = max(
                200,
                min(original_R, 1000),
            )

            # ----------------------------------------------------------
            # Test 1:
            # p = 0 must prevent all secondary propagation.
            # ----------------------------------------------------------

            zero_propagation = self.simulate_condition(
                p=0.0,
                tau=6,
                fn_rate=1.0,
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

            # ----------------------------------------------------------
            # Test 2:
            # Immediate perfect mediation must prevent propagation.
            # ----------------------------------------------------------

            perfect_mediation = self.simulate_condition(
                p=1.0,
                tau=0,
                fn_rate=0.0,
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

            # ----------------------------------------------------------
            # Test 3:
            # Certain propagation + complete detection failure must
            # escape the originating cell.
            # ----------------------------------------------------------

            uncontrolled = self.simulate_condition(
                p=1.0,
                tau=6,
                fn_rate=1.0,
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
                self.num_cells - 1,
            )

        finally:
            self.num_replicates = original_R

        print(
            "Computational verification checks passed."
        )

    # ------------------------------------------------------------------
    # ACTION TRACE
    # ------------------------------------------------------------------

    def write_illustrative_action_trace(self):
        """
        Write an illustrative audit record.

        Action Trace is primary.
        Reasoning information is supplementary and non-decisive.

        No claim of legal or NIST certification is made.
        """

        timestamp = (
            datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat()
        )

        trace = {
            "trace_role": (
                "illustrative simulation audit record"
            ),
            "timestamp": timestamp,
            "interval_id": self.exploit_interval,
            "originating_cell": "Protected_Series_Beta",
            "action_trace": [
                {
                    "event": "cross_boundary_action_attempt",
                    "status": "detected",
                },
                {
                    "event": "external_tool_invocation",
                    "status": "blocked",
                },
                {
                    "event": "cell_credentials",
                    "status": "revoked",
                },
                {
                    "event": "affected_cell",
                    "status": "isolated_for_review",
                },
            ],
            "reasoning_trace": {
                "role": "supplementary",
                "evidentiary_priority": "secondary",
                "summary": (
                    "Internal reasoning telemetry may assist "
                    "diagnosis but is not treated as the primary "
                    "evidence of executed behavior."
                ),
            },
        }

        canonical = json.dumps(
            trace,
            sort_keys=True,
            separators=(",", ":"),
        )

        trace["sha256_integrity_anchor"] = (
            hashlib.sha256(
                canonical.encode("utf-8")
            ).hexdigest()
        )

        path = os.path.join(
            self.registry_dir,
            "illustrative_action_trace.json",
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                trace,
                f,
                indent=2,
            )

        return path

    # ------------------------------------------------------------------
    # EXPORTS
    # ------------------------------------------------------------------

    def write_manifest(self):
        manifest = {
            "model_type": (
                "structured stochastic design experiment"
            ),
            "interpretive_status": (
                "illustrative; not calibrated to real-world "
                "agentic-AI failure frequencies"
            ),
            "seed": self.seed,
            "replicates_per_condition": self.num_replicates,
            "num_cells": self.num_cells,
            "sweep_horizon_steps": self.sweep_horizon,
            "systemic_contagion_definition": (
                "A run is classified as systemic contagion "
                "when compromise reaches at least "
                f"{self.systemic_secondary_threshold} "
                "cell(s) beyond the originating governance cell."
            ),
            "parameters": {
                "p": list(self.P_VALUES),
                "tau": list(self.TAU_VALUES),
                "fn_rate": list(self.FN_VALUES),
            },
            "outcomes": {
                "systemic_contagion_pct": (
                    "Percentage of replications in which "
                    "compromise crosses the specified "
                    "governance-cell threshold."
                ),
                "strategic_velocity_pct": (
                    "Percentage of secondary cell-capacity "
                    "remaining uncompromised over the "
                    "observation window."
                ),
                "propagated_exposure": (
                    "Mean number of secondary governance "
                    "cells reached by the adverse executable condition."
                ),
                "compromised_execution_persistence": (
                    "Mean cumulative active compromised "
                    "cell-steps across the observation window."
                ),
            },
            "fixed_dimensions": {
                "network_size": self.num_cells,
                "topology": (
                    "fully exposed potential cross-cell "
                    "interface; topology variation excluded"
                ),
                "self_healing": False,
                "nonlinear_sigmoid_leakage": False,
                "N_scaling": False,
            },
            "validity_claims": [
                "construct validity",
                "computational verification",
                "sensitivity robustness",
            ],
            "excluded_claim": (
                "empirical prediction of real-world "
                "failure frequency"
            ),
        }

        path = os.path.join(
            self.output_dir,
            "simulation_manifest.json",
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                manifest,
                f,
                indent=2,
            )

        return path

    def export_results(self):
        self.run_verification_checks()

        fixed_df = self.legacy_fixed_scenarios()

        fixed_path = os.path.join(
            self.output_dir,
            "legacy_fixed_scenario_anchor.csv",
        )

        fixed_df.to_csv(
            fixed_path,
            index=False,
        )

        sweep_df = self.run_parameter_sweep()

        sweep_path = os.path.join(
            self.output_dir,
            "parameter_sweep_196.csv",
        )

        sweep_df.to_csv(
            sweep_path,
            index=False,
        )

        # Marginal summaries are useful for compact manuscript tables.
        outcomes = [
            "systemic_contagion_pct",
            "strategic_velocity_pct",
            "propagated_exposure",
            "compromised_execution_persistence",
        ]

        marginal_p = (
            sweep_df
            .groupby("p", as_index=False)[outcomes]
            .mean()
        )

        marginal_tau = (
            sweep_df
            .groupby("tau", as_index=False)[outcomes]
            .mean()
        )

        marginal_fn = (
            sweep_df
            .groupby("fn_rate", as_index=False)[outcomes]
            .mean()
        )

        marginal_p.to_csv(
            os.path.join(
                self.output_dir,
                "marginal_by_p.csv",
            ),
            index=False,
        )

        marginal_tau.to_csv(
            os.path.join(
                self.output_dir,
                "marginal_by_tau.csv",
            ),
            index=False,
        )

        marginal_fn.to_csv(
            os.path.join(
                self.output_dir,
                "marginal_by_fn.csv",
            ),
            index=False,
        )

        manifest_path = self.write_manifest()

        trace_path = (
            self.write_illustrative_action_trace()
        )

        return {
            "sweep": sweep_df,
            "fixed": fixed_df,
            "sweep_path": sweep_path,
            "fixed_path": fixed_path,
            "manifest_path": manifest_path,
            "trace_path": trace_path,
        }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "MGE 196-condition robustness simulation."
        )
    )

    parser.add_argument(
        "--replicates",
        type=int,
        default=1000,
        help=(
            "Monte Carlo replications per parameter "
            "condition (default: 1000)."
        ),
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42).",
    )

    parser.add_argument(
        "--horizon",
        type=int,
        default=12,
        help=(
            "Containment observation window in "
            "simulation steps (default: 12)."
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./simulation_output",
        help="Directory for CSV and JSON outputs.",
    )

    args = parser.parse_args()

    simulator = ModelGovernanceEngineSimulator(
        num_replicates=args.replicates,
        seed=args.seed,
        sweep_horizon=args.horizon,
        output_dir=args.output_dir,
    )

    outputs = simulator.export_results()

    print()
    print("=" * 72)
    print("MGE ROBUSTNESS ANALYSIS COMPLETED")
    print("=" * 72)
    print(
        f"Parameter conditions : "
        f"{len(outputs['sweep'])}"
    )
    print(
        f"Replications/condition: "
        f"{args.replicates}"
    )
    print(
        f"Total stochastic runs : "
        f"{len(outputs['sweep']) * args.replicates:,}"
    )
    print(
        f"Sweep results         : "
        f"{outputs['sweep_path']}"
    )
    print(
        f"Legacy anchor         : "
        f"{outputs['fixed_path']}"
    )
    print(
        f"Model manifest        : "
        f"{outputs['manifest_path']}"
    )
    print(
        f"Action Trace          : "
        f"{outputs['trace_path']}"
    )
    print("=" * 72)

    # Print the revised stochastic version of the parameter combination
    # previously labelled "Adversarial Stress".
    sweep = outputs["sweep"]

    adversarial = sweep[
        np.isclose(sweep["p"], 0.010)
        & (sweep["tau"] == 5)
        & np.isclose(sweep["fn_rate"], 0.20)
    ]

    if len(adversarial) == 1:
        row = adversarial.iloc[0]

        print()
        print(
            "STOCHASTIC RE-EVALUATION OF "
            "LEGACY ADVERSARIAL-STRESS PARAMETERS"
        )
        print("-" * 72)
        print(
            f"Systemic contagion    : "
            f"{row['systemic_contagion_pct']:.2f}% "
            f"[{row['systemic_contagion_ci_low']:.2f}, "
            f"{row['systemic_contagion_ci_high']:.2f}]"
        )
        print(
            f"Strategic velocity    : "
            f"{row['strategic_velocity_pct']:.2f}%"
        )
        print(
            f"Propagated exposure   : "
            f"{row['propagated_exposure']:.3f} "
            "secondary cells"
        )
        print(
            f"CEP                   : "
            f"{row['compromised_execution_persistence']:.3f} "
            "compromised cell-steps"
        )


if __name__ == "__main__":
    main()

    
