from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

from solver import SimulationResult


def ensure_output_dir(path: str | Path) -> Path:
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _temperature_limits(result: SimulationResult) -> tuple[float, float]:
    values = [frame for frame in result.snapshots]
    values.extend(result.animation_frames)
    vmin = min(float(np.min(frame)) for frame in values)
    vmax = max(float(np.max(frame)) for frame in values)
    if result.stop_reason is not None and vmin < result.boundary_temperature:
        vmin = result.boundary_temperature
    return vmin, vmax


def plot_heatmap_snapshots(
    result: SimulationResult,
    output_dir: str | Path,
    title: str,
) -> Path:
    """Save heatmaps at selected times in one figure."""
    output_dir = ensure_output_dir(output_dir)
    vmin, vmax = _temperature_limits(result)
    count = len(result.snapshots)
    cols = min(3, count)
    rows = int(np.ceil(count / cols))

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(4.8 * cols, 4.2 * rows),
        constrained_layout=True,
    )
    axes_array = np.atleast_1d(axes).ravel()

    image = None
    for ax, snapshot, time_value in zip(
        axes_array, result.snapshots, result.snapshot_times
    ):
        image = ax.imshow(snapshot, cmap="inferno", vmin=vmin, vmax=vmax, origin="lower")
        ax.contour(result.core_mask, levels=[0.5], colors="cyan", linewidths=1.0)
        ax.set_title(f"t = {time_value:.2f} s")
        ax.set_xlabel("x grid index")
        ax.set_ylabel("y grid index")

    for ax in axes_array[count:]:
        ax.axis("off")

    if image is not None:
        cbar = fig.colorbar(image, ax=axes_array[:count], shrink=0.9)
        cbar.set_label("Temperature (deg C)")

    fig.suptitle(title)
    path = output_dir / f"{result.scenario_name}_heatmap_snapshots.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_final_heatmap(
    result: SimulationResult,
    output_dir: str | Path,
    title: str,
) -> Path:
    output_dir = ensure_output_dir(output_dir)
    final_temperature = result.snapshots[-1]
    vmin, vmax = _temperature_limits(result)

    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(
        final_temperature,
        cmap="inferno",
        vmin=vmin,
        vmax=vmax,
        origin="lower",
    )
    ax.contour(result.core_mask, levels=[0.5], colors="cyan", linewidths=1.0)
    ax.set_title(f"{title} - Final Temperature")
    ax.set_xlabel("x grid index")
    ax.set_ylabel("y grid index")
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Temperature (deg C)")
    fig.tight_layout()

    path = output_dir / f"{result.scenario_name}_final_heatmap.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_tmax(
    result: SimulationResult,
    output_dir: str | Path,
    title: str,
) -> Path:
    output_dir = ensure_output_dir(output_dir)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(result.times, result.tmax, linewidth=2)
    ax.set_title(f"{title} - Maximum Temperature")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Tmax (deg C)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    path = output_dir / f"{result.scenario_name}_tmax.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def create_animation(
    result: SimulationResult,
    output_dir: str | Path,
    title: str,
    fps: int = 12,
) -> Path:
    """Save a GIF animation of the heat spreading through the chip."""
    output_dir = ensure_output_dir(output_dir)
    vmin, vmax = _temperature_limits(result)

    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(
        result.animation_frames[0],
        cmap="inferno",
        vmin=vmin,
        vmax=vmax,
        origin="lower",
        animated=True,
    )
    ax.contour(result.core_mask, levels=[0.5], colors="cyan", linewidths=1.0)
    ax.set_xlabel("x grid index")
    ax.set_ylabel("y grid index")
    cbar = fig.colorbar(image, ax=ax)
    cbar.set_label("Temperature (deg C)")

    frame_dt = result.dt * max(
        1,
        int(round(len(result.times) / max(1, len(result.animation_frames)))),
    )

    def update(frame_index: int):
        image.set_array(result.animation_frames[frame_index])
        ax.set_title(f"{title} - t ~ {frame_index * frame_dt:.2f} s")
        return (image,)

    animation = FuncAnimation(
        fig,
        update,
        frames=len(result.animation_frames),
        interval=1000 / fps,
        blit=False,
    )

    path = output_dir / f"{result.scenario_name}_animation.gif"
    animation.save(path, writer=PillowWriter(fps=fps))
    plt.close(fig)
    return path


def plot_scenario_comparison(
    results: list[SimulationResult],
    output_dir: str | Path,
) -> Path:
    """Compare maximum temperature curves from all scenarios."""
    output_dir = ensure_output_dir(output_dir)

    fig, ax = plt.subplots(figsize=(8, 5))
    for result in results:
        ax.plot(result.times, result.tmax, linewidth=2, label=result.scenario_name)

    ax.set_title("Scenario Comparison - Maximum Temperature")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Tmax (deg C)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    path = output_dir / "comparison_tmax.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_convergence_study(
    study_name: str,
    rows: list[dict],
    output_dir: str | Path,
) -> Path:
    """Plot final Tmax from grid or time convergence rows."""
    output_dir = ensure_output_dir(output_dir)

    if study_name == "grid_convergence":
        x_values = [row["grid_size"] for row in rows]
        x_label = "Grid size N"
        title = "Grid Convergence - Final Maximum Temperature"
    elif study_name == "time_convergence":
        x_values = [row["dt"] for row in rows]
        x_label = "Time step dt (s)"
        title = "Time Convergence - Final Maximum Temperature"
    else:
        raise ValueError(f"Unknown convergence study: {study_name}")

    y_values = [row["tmax_final"] for row in rows]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(x_values, y_values, marker="o", linewidth=2)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Final Tmax (deg C)")
    ax.grid(True, alpha=0.3)

    if study_name == "time_convergence":
        ax.invert_xaxis()

    for x_value, y_value in zip(x_values, y_values):
        ax.annotate(
            f"{y_value:.2f}",
            xy=(x_value, y_value),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=9,
        )

    fig.tight_layout()
    path = output_dir / f"{study_name}.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path
