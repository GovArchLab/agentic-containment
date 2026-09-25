#!/usr/bin/env python3
"""
Static terminology and public-release audit for
mge_simulation_full_robustness.py.

This script does not modify the target.

It verifies that:
- the Python source parses;
- PE/CEP stochastic terminology is present;
- obsolete stochastic VM/VS identifiers and keys are absent;
- rejected-manuscript legacy anchor code is absent;
- obsolete legacy manifest metadata is absent;
- strategic_velocity_pct occurs exactly once in the simulation
  return dictionary.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
from pathlib import Path


FORBIDDEN_TERMS = [
    "value_missing_runs",
    "missing_mean",
    "missing_mcse",
    "value_slippage_runs",
    "slippage_mean",
    "slippage_mcse",
    "throughput_runs",
    "throughput_mean",
    "throughput_mcse",

    "accumulated_value_missing",
    "value_missing_mcse",
    "value_slippage",
    "value_slippage_mcse",

    "accumulated_value_missing_usd",
    "value_slippage_usd",

    "legacy_fixed_scenarios",
    "legacy_fixed_scenario_anchor",
    "nonlinear_sigmoid_leakage",
]

EXPECTED_NEW_KEYS = [
    "propagated_exposure",
    "propagated_exposure_mcse",
    "compromised_execution_persistence",
    "compromised_execution_persistence_mcse",
]

EXPECTED_INTERNAL_NAMES = [
    "propagated_exposure_runs",
    "pe_mean",
    "pe_mcse",
    "cep_runs",
    "cep_mean",
    "cep_mcse",
    "strategic_velocity_runs",
    "strategic_velocity_mean",
    "strategic_velocity_mcse",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def quoted_key_count(
    source: str,
    key: str,
) -> int:

    pattern = (
        rf'["\']{re.escape(key)}["\']'
    )

    return len(
        re.findall(
            pattern,
            source,
        )
    )


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Audit terminology and public-release state "
            "of mge_simulation_full_robustness.py."
        )
    )

    parser.add_argument(
        "target",
        nargs="?",
        default="mge_simulation_full_robustness.py",
    )

    args = parser.parse_args()

    target = Path(
        args.target
    ).resolve()

    if not target.exists():
        raise FileNotFoundError(target)

    source = target.read_text(
        encoding="utf-8"
    )

    print("=" * 72)
    print("MGE PUBLIC-RELEASE TERMINOLOGY AUDIT")
    print("=" * 72)

    print(f"Target : {target}")
    print(
        f"SHA256 : {sha256_file(target)}"
    )

    print()

    failures = []

    # ------------------------------------------------------------
    # Parse
    # ------------------------------------------------------------

    try:
        tree = ast.parse(source)

    except SyntaxError as exc:

        raise SystemExit(
            f"[FAIL] Python syntax error: {exc}"
        )

    print(
        "[PASS] Python source parses successfully."
    )

    # ------------------------------------------------------------
    # Legacy / obsolete terminology
    # ------------------------------------------------------------

    source_lower = source.lower()

    for term in FORBIDDEN_TERMS:

        if term.lower() in source_lower:

            failures.append(
                f"Forbidden legacy/stochastic term remains: "
                f"{term!r}"
            )

    if "adversarial stress" in source_lower:

        failures.append(
            "Old 'Adversarial Stress' scenario wording remains."
        )

    # ------------------------------------------------------------
    # Required new terminology
    # ------------------------------------------------------------

    for name in EXPECTED_INTERNAL_NAMES:

        if name not in source:

            failures.append(
                f"Expected PE/CEP internal name "
                f"{name!r} not found."
            )

    for key in EXPECTED_NEW_KEYS:

        if quoted_key_count(
            source,
            key,
        ) == 0:

            failures.append(
                f"Expected PE/CEP output key "
                f"{key!r} not found."
            )

    # ------------------------------------------------------------
    # simulate_condition return dictionary
    # ------------------------------------------------------------

    simulate_nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(
            node,
            ast.FunctionDef,
        )
        and node.name == "simulate_condition"
    ]

    if len(simulate_nodes) != 1:

        failures.append(
            "Could not uniquely identify simulate_condition()."
        )

    else:

        fn = simulate_nodes[0]

        return_dicts = [
            node.value
            for node in ast.walk(fn)
            if isinstance(
                node,
                ast.Return,
            )
            and isinstance(
                node.value,
                ast.Dict,
            )
        ]

        if len(return_dicts) != 1:

            failures.append(
                "Expected exactly one dictionary return "
                "in simulate_condition()."
            )

        else:

            keys = []

            for key_node in return_dicts[0].keys:

                if (
                    isinstance(
                        key_node,
                        ast.Constant,
                    )
                    and isinstance(
                        key_node.value,
                        str,
                    )
                ):
                    keys.append(
                        key_node.value
                    )

            if (
                keys.count(
                    "strategic_velocity_pct"
                )
                != 1
            ):

                failures.append(
                    "strategic_velocity_pct must occur "
                    "exactly once in the simulation return."
                )

            for key in EXPECTED_NEW_KEYS:

                if keys.count(key) != 1:

                    failures.append(
                        f"{key!r} must occur exactly once "
                        "in the simulation return."
                    )

    # ------------------------------------------------------------
    # Report
    # ------------------------------------------------------------

    print()

    if failures:

        print("FAILURES")
        print("-" * 72)

        for failure in failures:

            print(
                f"[FAIL] {failure}"
            )

        print()
        print("=" * 72)

        print(
            f"AUDIT FAILED: "
            f"{len(failures)} issue(s) found."
        )

        print("=" * 72)

        raise SystemExit(1)

    print("=" * 72)
    print("AUDIT PASSED")
    print("=" * 72)

    print(
        "No rejected-manuscript legacy anchor code or "
        "obsolete stochastic VM/VS proxy terminology was found."
    )

    print(
        "PE/CEP internal names and output keys are present."
    )

    print(
        "strategic_velocity_pct occurs exactly once in "
        "the simulation return dictionary."
    )

    print("=" * 72)


if __name__ == "__main__":
    main()
