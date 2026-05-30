from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SimulationResult:
    """Container for the numerical solution and useful diagnostics."""

    scenario_name: str
    times: np.ndarray
    snapshots: list[np.ndarray]
    snapshot_times: list[float]
    animation_frames: list[np.ndarray]
    tmax: np.ndarray
    core_mask: np.ndarray
    q: np.ndarray
    dx: float
    dt: float
    r: float
    cooling_rate: float
    boundary_temperature: float


def create_core_mask(grid_size: int, core_fraction: float) -> np.ndarray:
    """Create a square CPU core mask centered in the chip."""
    if not 0.0 < core_fraction < 1.0:
        raise ValueError("core_fraction must be between 0 and 1.")

    mask = np.zeros((grid_size, grid_size), dtype=bool)
    core_size = max(1, int(round(grid_size * core_fraction)))
    start = (grid_size - core_size) // 2
    end = start + core_size
    mask[start:end, start:end] = True
    return mask


def apply_boundary(u: np.ndarray, boundary_temperature: float) -> None:
    """Keep the four chip edges fixed at the cooling temperature."""
    u[0, :] = boundary_temperature
    u[-1, :] = boundary_temperature
    u[:, 0] = boundary_temperature
    u[:, -1] = boundary_temperature


def solve_heat_equation(
    *,
    scenario_name: str,
    grid_size: int,
    chip_size: float,
    alpha: float,
    q_strength: float,
    core_fraction: float,
    dt: float,
    total_time: float,
    initial_temperature: float,
    boundary_temperature: float,
    cooling_rate: float,
    snapshot_times: list[float],
    animation_stride: int,
) -> SimulationResult:
    """Solve the 2D heat equation with an explicit finite difference method.

    The update formula is

        U_new[i, j] = U[i, j] + r * neighbor_sum + dt * Q[i, j]

    A simple optional cooling term is also included:

        -dt * cooling_rate * (U[i, j] - boundary_temperature)

    Use cooling_rate = 0 for the pure heat equation with only cooled edges.

    where r = alpha * dt / dx^2 and neighbor_sum is the difference between
    the four neighbor temperatures and 4 times the current temperature.
    """
    if grid_size < 3:
        raise ValueError("grid_size must be at least 3.")
    if dt <= 0 or total_time <= 0:
        raise ValueError("dt and total_time must be positive.")

    dx = chip_size / (grid_size - 1)
    r = alpha * dt / (dx * dx)
    if r > 0.25:
        stable_dt = 0.25 * dx * dx / alpha
        raise ValueError(
            f"Unstable explicit scheme for scenario '{scenario_name}': "
            f"r = {r:.4f} > 0.25. Use dt <= {stable_dt:.6g}."
        )

    steps = int(round(total_time / dt))
    times = np.linspace(0.0, steps * dt, steps + 1)

    u = np.full((grid_size, grid_size), initial_temperature, dtype=float)
    apply_boundary(u, boundary_temperature)

    core_mask = create_core_mask(grid_size, core_fraction)
    q = np.zeros_like(u)
    q[core_mask] = q_strength

    wanted_snapshots = sorted(set([0.0, total_time, *snapshot_times]))
    snapshot_indices = {
        min(steps, max(0, int(round(t / dt)))) for t in wanted_snapshots
    }

    snapshots: list[np.ndarray] = []
    stored_snapshot_times: list[float] = []
    animation_frames: list[np.ndarray] = []
    tmax = np.empty(steps + 1, dtype=float)

    for step in range(steps + 1):
        current_time = step * dt
        tmax[step] = float(np.max(u))

        if step in snapshot_indices:
            snapshots.append(u.copy())
            stored_snapshot_times.append(current_time)

        if step % animation_stride == 0 or step == steps:
            animation_frames.append(u.copy())

        if step == steps:
            break

        u_new = u.copy()
        u_new[1:-1, 1:-1] = (
            u[1:-1, 1:-1]
            + r
            * (
                u[2:, 1:-1]
                + u[:-2, 1:-1]
                + u[1:-1, 2:]
                + u[1:-1, :-2]
                - 4.0 * u[1:-1, 1:-1]
            )
            + dt * q[1:-1, 1:-1]
            - dt * cooling_rate * (u[1:-1, 1:-1] - boundary_temperature)
        )

        apply_boundary(u_new, boundary_temperature)
        u = u_new

    return SimulationResult(
        scenario_name=scenario_name,
        times=times,
        snapshots=snapshots,
        snapshot_times=stored_snapshot_times,
        animation_frames=animation_frames,
        tmax=tmax,
        core_mask=core_mask,
        q=q,
        dx=dx,
        dt=dt,
        r=r,
        cooling_rate=cooling_rate,
        boundary_temperature=boundary_temperature,
    )
