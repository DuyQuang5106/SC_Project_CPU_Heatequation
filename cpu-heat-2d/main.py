from __future__ import annotations

from pathlib import Path

from scenarios import get_scenarios
from solver import solve_heat_equation
from visualization import (
    create_animation,
    ensure_output_dir,
    plot_final_heatmap,
    plot_heatmap_snapshots,
    plot_scenario_comparison,
    plot_tmax,
)


def run_project() -> None:
    output_root = ensure_output_dir("outputs")
    results = []

    for scenario in get_scenarios():
        name = scenario["name"]
        title = scenario["title"]
        scenario_output = output_root / name
        ensure_output_dir(scenario_output)

        print(f"Running scenario: {name}")
        result = solve_heat_equation(
            scenario_name=name,
            grid_size=scenario["grid_size"],
            chip_size=scenario["chip_size"],
            alpha=scenario["alpha"],
            q_strength=scenario["q_strength"],
            core_fraction=scenario["core_fraction"],
            dt=scenario["dt"],
            total_time=scenario["total_time"],
            initial_temperature=scenario["initial_temperature"],
            boundary_temperature=scenario["boundary_temperature"],
            cooling_rate=scenario["cooling_rate"],
            snapshot_times=scenario["snapshot_times"],
            animation_stride=scenario["animation_stride"],
        )
        results.append(result)

        plot_heatmap_snapshots(result, scenario_output, title)
        plot_final_heatmap(result, scenario_output, title)
        plot_tmax(result, scenario_output, title)
        create_animation(result, scenario_output, title)

        print(
            f"  r = {result.r:.4f}, "
            f"final Tmax = {result.tmax[-1]:.2f} deg C, "
            f"saved to {Path(scenario_output)}"
        )

    comparison_path = plot_scenario_comparison(results, output_root)
    print(f"Saved comparison plot: {comparison_path}")
    print("Done. Check the outputs folder.")


if __name__ == "__main__":
    run_project()
