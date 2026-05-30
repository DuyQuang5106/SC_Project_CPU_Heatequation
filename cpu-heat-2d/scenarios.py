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
    ]
    return scenarios
