from __future__ import annotations


BASE_SCENARIO = {
    "grid_size": 80,
    "chip_size": 1.0,
    "alpha": 8.0e-4,
    "q_strength": 28.0,
    "core_fraction": 0.25,
    "dt": 0.02,
    "total_time": 8.0,
    "initial_temperature": 25.0,
    "boundary_temperature": 25.0,
    "cooling_rate": 0.0,
    "boundary_condition": "dirichlet",
    "boundary_cooling_rate": 0.0,
    "snapshot_times": [1.0, 2.0, 4.0, 8.0],
    "animation_stride": 5,
}


def get_scenarios() -> list[dict]:
    """Return simulation scenarios for load, cooling, and material comparison."""
    scenarios = [
        {
            **BASE_SCENARIO,
            "name": "low_load",
            "title": "Low CPU Load",
            "q_strength": 14.0,
        },
        {
            **BASE_SCENARIO,
            "name": "high_load",
            "title": "High CPU Load",
            "q_strength": 45.0,
        },
        {
            **BASE_SCENARIO,
            "name": "weak_cooling",
            "title": "Weak Cooling",
            "cooling_rate": 0.01,
        },
        {
            **BASE_SCENARIO,
            "name": "strong_cooling",
            "title": "Strong Cooling",
            "cooling_rate": 0.08,
        },
        {
            **BASE_SCENARIO,
            "name": "low_alpha",
            "title": "Low Alpha Material",
            "alpha": 4.0e-4,
        },
        {
            **BASE_SCENARIO,
            "name": "high_alpha",
            "title": "High Alpha Material",
            "alpha": 1.2e-3,
        },
        {
            **BASE_SCENARIO,
            "name": "robin_boundary_cooling",
            "title": "Robin Boundary Cooling",
            "boundary_condition": "robin",
            "boundary_cooling_rate": 1.5,
        },
    ]
    return scenarios


def get_grid_convergence_scenarios() -> list[dict]:
    """Return scenarios for checking how grid resolution affects Tmax."""
    scenarios = []
    for grid_size in [40, 80, 120]:
        scenarios.append(
            {
                **BASE_SCENARIO,
                "name": f"grid_{grid_size}",
                "title": f"Grid Convergence N={grid_size}",
                "grid_size": grid_size,
                "animation_stride": 10,
            }
        )
    return scenarios


def get_time_convergence_scenarios() -> list[dict]:
    """Return scenarios for checking how time step size affects Tmax."""
    scenarios = []
    for dt in [0.04, 0.02, 0.01]:
        scenarios.append(
            {
                **BASE_SCENARIO,
                "name": f"dt_{str(dt).replace('.', '_')}",
                "title": f"Time Convergence dt={dt}",
                "dt": dt,
                "animation_stride": max(1, int(round(0.1 / dt))),
            }
        )
    return scenarios


def get_stability_experiment_scenario() -> dict:
    """Return one intentionally unstable setup to demonstrate r > 1/4."""
    return {
        **BASE_SCENARIO,
        "name": "unstable_large_dt",
        "title": "Stability Experiment: r > 1/4",
        "dt": 0.06,
    }
