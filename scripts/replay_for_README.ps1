param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

# Run from repository root even though this script lives in scripts/.
$RepoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $RepoRoot

try {

    function Invoke-PythonStep {
        param(
            [string]$Label,
            [string[]]$Arguments
        )

        Write-Host ""
        Write-Host ("=" * 72)
        Write-Host $Label
        Write-Host ("=" * 72)

        & $Python @Arguments

        if ($LASTEXITCODE -ne 0) {
            throw "$Label failed with exit code $LASTEXITCODE."
        }
    }

    Invoke-PythonStep `
        "1. STOCHASTIC PARAMETER SWEEP" `
        @(
            ".\mge_simulation_full_robustness.py",
            "--replicates", "1000",
            "--seed", "42"
        )

    Invoke-PythonStep `
        "2. CONTAINMENT ENVELOPE" `
        @(
            ".\make_containment_envelope.py",
            "--input",
            ".\simulation_output\parameter_sweep_196.csv",
            "--outdir",
            ".\figures"
        )

    Invoke-PythonStep `
        "3. BOUNDED LEAKAGE GAP — CLEAN" `
        @(
            ".\make_bounded_leakage_gap.py",
            "--input",
            ".\simulation_output\parameter_sweep_196.csv",
            "--outdir",
            ".\figures"
        )

    Invoke-PythonStep `
        "4. BOUNDED LEAKAGE GAP — ANNOTATED" `
        @(
            ".\make_bounded_leakage_gap.py",
            "--input",
            ".\simulation_output\parameter_sweep_196.csv",
            "--outdir",
            ".\figures",
            "--annotate"
        )

    Invoke-PythonStep `
        "5. MARGINAL EFFECTS AND LATEX ARTIFACTS" `
        @(
            ".\make_marginal_effects.py",
            "--input",
            ".\simulation_output\parameter_sweep_196.csv"
        )

    Invoke-PythonStep `
        "6. PUBLIC TERMINOLOGY AUDIT" `
        @(
            ".\tools\audit_mge_terminology.py"
        )

    $ExpectedFiles = @(
        ".\simulation_output\parameter_sweep_196.csv",
        ".\simulation_output\simulation_manifest.json",
        ".\simulation_output\forensic_registry\illustrative_action_trace.json",
        ".\simulation_output\marginals\marginal_by_p.csv",
        ".\simulation_output\marginals\marginal_by_tau.csv",
        ".\simulation_output\marginals\marginal_by_fn.csv",
        ".\simulation_output\marginals\marginal_effects_paragraph.tex",
        ".\simulation_output\marginals\marginal_means_full.tex",
        ".\simulation_output\marginals\marginal_contrasts.tex",
        ".\figures\containment_envelope.pdf",
        ".\figures\containment_envelope.png",
        ".\figures\bounded_leakage_gap.pdf",
        ".\figures\bounded_leakage_gap.png",
        ".\figures\bounded_leakage_gap_annotated.pdf",
        ".\figures\bounded_leakage_gap_annotated.png"
    )

    foreach ($Path in $ExpectedFiles) {

        if (-not (Test-Path -LiteralPath $Path)) {
            throw "Expected replay artifact missing: $Path"
        }
    }

    Write-Host ""
    Write-Host ("=" * 72)
    Write-Host "REPRODUCTION COMPLETED SUCCESSFULLY"
    Write-Host ("=" * 72)
    Write-Host "[PASS] Simulation completed."
    Write-Host "[PASS] Figures regenerated."
    Write-Host "[PASS] Marginal artifacts regenerated."
    Write-Host "[PASS] Public terminology audit passed."
    Write-Host "[PASS] Expected output files are present."
    Write-Host ("=" * 72)
}
finally {
    Pop-Location
}
