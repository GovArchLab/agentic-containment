import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def build_containment_envelope(
    csv_path,
    outdir="figures",
    value_col="systemic_contagion_pct",
    pdf_name="containment_envelope.pdf",
    png_name="containment_envelope.png",
):
    df = pd.read_csv(csv_path)

    required_cols = {"p", "tau", "fn_rate", value_col}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    os.makedirs(outdir, exist_ok=True)

    p_values = [0.001, 0.005, 0.010, 0.020]
    tau_values = sorted(df["tau"].unique())
    fn_values = sorted(df["fn_rate"].unique())

    vmin = df[value_col].min()
    vmax = df[value_col].max()

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(12, 9),
        constrained_layout=True,
        sharex=True,
        sharey=True,
    )

    axes = axes.flatten()

    cmap = plt.cm.Blues

    for ax, p in zip(axes, p_values):
        sub = df[np.isclose(df["p"], p)].copy()

        pivot = (
            sub.pivot(index="tau", columns="fn_rate", values=value_col)
            .reindex(index=tau_values, columns=fn_values)
        )

        Z = pivot.values

        im = ax.imshow(
            Z,
            origin="lower",
            aspect="auto",
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
        )

        ax.set_title(rf"$p = {p:.3f}$", fontsize=12, pad=8)

        ax.set_xticks(range(len(fn_values)))
        ax.set_xticklabels([f"{int(x*100)}" for x in fn_values], fontsize=10)

        ax.set_yticks(range(len(tau_values)))
        ax.set_yticklabels([str(int(x)) for x in tau_values], fontsize=10)

        ax.set_xlabel("False-negative rate FN (%)", fontsize=10)
        ax.set_ylabel(r"Mediation delay $\tau$", fontsize=10)

        # cell borders
        ax.set_xticks(np.arange(-0.5, len(fn_values), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(tau_values), 1), minor=True)
        ax.grid(which="minor", color="white", linestyle="-", linewidth=1.0)
        ax.tick_params(which="minor", bottom=False, left=False)

        # annotate cells
        threshold = (vmin + vmax) / 2.0
        for i in range(len(tau_values)):
            for j in range(len(fn_values)):
                val = Z[i, j]
                color = "white" if val > threshold else "black"
                ax.text(
                    j,
                    i,
                    f"{val:.1f}",
                    ha="center",
                    va="center",
                    fontsize=8.5,
                    color=color,
                )

        # optional contour lines
        X, Y = np.meshgrid(np.arange(len(fn_values)), np.arange(len(tau_values)))
        contour_levels = [5, 10, 15]
        valid_levels = [lv for lv in contour_levels if vmin < lv < vmax]
        if valid_levels:
            cs = ax.contour(
                X,
                Y,
                Z,
                levels=valid_levels,
                colors="black",
                linewidths=0.8,
                alpha=0.7,
            )
            ax.clabel(cs, inline=True, fontsize=7, fmt="%.0f")

    cbar = fig.colorbar(
        im,
        ax=axes,
        shrink=0.92,
        pad=0.02,
    )
    cbar.set_label("Systemic contagion rate (%)", fontsize=11)

    fig.suptitle(
        "Conditional Containment Envelope",
        fontsize=15,
        y=1.02,
    )

    pdf_path = os.path.join(outdir, pdf_name)
    png_path = os.path.join(outdir, png_name)

    fig.savefig(pdf_path, dpi=300, bbox_inches="tight")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved PDF: {pdf_path}")
    print(f"Saved PNG: {png_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create containment envelope figure from parameter_sweep_196.csv"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="./simulation_output/parameter_sweep_196.csv",
        help="Path to parameter_sweep_196.csv",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default="./figures",
        help="Output directory for figures",
    )
    args = parser.parse_args()

    build_containment_envelope(
        csv_path=args.input,
        outdir=args.outdir,
    )

    
