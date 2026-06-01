from __future__ import annotations

import csv
from pathlib import Path

from scenarios import (
    get_grid_convergence_scenarios,
    get_scenarios,
    get_stability_experiment_scenario,
    get_time_convergence_scenarios,
    get_unstable_blowup_scenario,
)
from solver import solve_heat_equation
from visualization import (
    create_animation,
    ensure_output_dir,
    plot_convergence_study,
    plot_final_heatmap,
    plot_heatmap_snapshots,
    plot_scenario_comparison,
    plot_tmax,
)


def solve_scenario(scenario: dict):
    return solve_heat_equation(
        scenario_name=scenario["name"],
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
        boundary_condition=scenario["boundary_condition"],
        boundary_cooling_rate=scenario["boundary_cooling_rate"],
        snapshot_times=scenario["snapshot_times"],
        animation_stride=scenario["animation_stride"],
        enforce_stability=scenario.get("enforce_stability", True),
        checkerboard_perturbation=scenario.get("checkerboard_perturbation", 0.0),
        stop_temperature_limit=scenario.get("stop_temperature_limit"),
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_project() -> None:
    output_root = ensure_output_dir("outputs")
    results = []

    for scenario in get_scenarios():
        name = scenario["name"]
        title = scenario["title"]
        scenario_output = output_root / name
        ensure_output_dir(scenario_output)

        print(f"Running scenario: {name}")
        result = solve_scenario(scenario)
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
    run_unstable_blowup_demo(output_root)
    run_numerical_studies(output_root)
    print("Done. Check the outputs folder.")


def run_unstable_blowup_demo(output_root: Path) -> None:
    scenario = get_unstable_blowup_scenario()
    name = scenario["name"]
    title = scenario["title"]
    scenario_output = output_root / name
    ensure_output_dir(scenario_output)

    print(f"Running unstable error blow-up demo: {name}")
    result = solve_scenario(scenario)

    plot_heatmap_snapshots(result, scenario_output, title)
    plot_final_heatmap(result, scenario_output, title)
    plot_tmax(result, scenario_output, title)
    create_animation(result, scenario_output, title)

    report_path = scenario_output / f"{name}_report.txt"
    report = (
        "Unstable error blow-up demo\n"
        "===========================\n\n"
        "This run intentionally disables the stability guard and uses r > 1/4.\n"
        "A tiny checkerboard perturbation is added to the initial temperature field\n"
        "so the unstable high-frequency error mode becomes visible.\n\n"
        f"grid_size: {scenario['grid_size']}\n"
        f"dt: {result.dt}\n"
        f"dx: {result.dx}\n"
        f"r: {result.r:.6f}\n"
        f"checkerboard_perturbation: {scenario['checkerboard_perturbation']}\n"
        f"final_recorded_time: {result.times[-1]:.4f} s\n"
        f"final_recorded_Tmax: {result.tmax[-1]:.6g} deg C\n"
        f"stop_reason: {result.stop_reason or 'completed full requested time'}\n"
    )
    report_path.write_text(report, encoding="utf-8")

    print(
        f"  r = {result.r:.4f}, "
        f"final recorded Tmax = {result.tmax[-1]:.2f} deg C, "
        f"saved to {Path(scenario_output)}"
    )


def run_numerical_studies(output_root: Path) -> None:
    studies_output = ensure_output_dir(output_root / "numerical_studies")
    convergence_rows: list[dict] = []

    for study_name, scenarios in [
        ("grid_convergence", get_grid_convergence_scenarios()),
        ("time_convergence", get_time_convergence_scenarios()),
    ]:
        print(f"Running numerical study: {study_name}")
        study_rows = []
        for scenario in scenarios:
            result = solve_scenario(scenario)
            row = {
                "study": study_name,
                "scenario": scenario["name"],
                "grid_size": scenario["grid_size"],
                "dt": scenario["dt"],
                "dx": result.dx,
                "r": result.r,
                "tmax_final": float(result.tmax[-1]),
            }
            study_rows.append(row)
            convergence_rows.append(row)
            print(
                f"  {scenario['name']}: "
                f"grid={scenario['grid_size']}, dt={scenario['dt']}, "
                f"r={result.r:.4f}, final Tmax={result.tmax[-1]:.2f} deg C"
            )

        plot_path = plot_convergence_study(study_name, study_rows, studies_output)
        print(f"  saved plot: {plot_path}")

    csv_path = studies_output / "convergence_summary.csv"
    write_csv(csv_path, convergence_rows)
    print(f"Saved convergence summary: {csv_path}")

    print("Running numerical study: stability_experiment")
    unstable = get_stability_experiment_scenario()
    report_path = studies_output / "stability_experiment.txt"
    try:
        solve_scenario(unstable)
    except ValueError as error:
        report = (
            "Stability experiment\n"
            "====================\n\n"
            "This scenario intentionally uses a large dt so that r > 1/4.\n"
            "The solver rejects it before running because the explicit 2D heat\n"
            "scheme would be numerically unstable.\n\n"
            f"Caught error:\n{error}\n"
        )
        report_path.write_text(report, encoding="utf-8")
        print(f"  expected instability caught; saved report: {report_path}")
    else:
        report_path.write_text(
            "The unstable scenario did not raise an error.\n",
            encoding="utf-8",
        )
        print(f"  warning: unstable scenario did not raise an error.")


if __name__ == "__main__":
    run_project()
