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
    boundary_condition: str
    boundary_cooling_rate: float
    stop_reason: str | None = None


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


def create_boundary_mask(grid_size: int) -> np.ndarray:
    """Create a mask for the four chip edges."""
    mask = np.zeros((grid_size, grid_size), dtype=bool)
    mask[0, :] = True
    mask[-1, :] = True
    mask[:, 0] = True
    mask[:, -1] = True
    return mask


def apply_dirichlet_boundary(u: np.ndarray, boundary_temperature: float) -> None:
    """Keep the four chip edges fixed at the cooling temperature."""
    u[0, :] = boundary_temperature
    u[-1, :] = boundary_temperature
    u[:, 0] = boundary_temperature
    u[:, -1] = boundary_temperature


def laplacian_with_insulated_outer_edge(u: np.ndarray) -> np.ndarray:
    """Compute a 2D Laplacian using zero-flux ghost values outside the chip."""
    padded = np.pad(u, pad_width=1, mode="edge")
    return (
        padded[2:, 1:-1]
        + padded[:-2, 1:-1]
        + padded[1:-1, 2:]
        + padded[1:-1, :-2]
        - 4.0 * u
    )


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
    boundary_condition: str = "dirichlet",
    boundary_cooling_rate: float = 0.0,
    enforce_stability: bool = True,
    checkerboard_perturbation: float = 0.0,
    stop_temperature_limit: float | None = None,
) -> SimulationResult:
    """Solve the 2D heat equation with an explicit finite difference method.

    The update formula is

        U_new[i, j] = U[i, j] + r * neighbor_sum + dt * Q[i, j]

    A simple optional internal cooling term is also included:

        -dt * cooling_rate * (U[i, j] - boundary_temperature)

    For boundary_condition = "dirichlet", the four edges are fixed at
    boundary_temperature. For boundary_condition = "robin", the edges are not
    fixed; instead they lose heat by a Newton/Robin cooling term proportional
    to their temperature difference from boundary_temperature.

    where r = alpha * dt / dx^2 and neighbor_sum is the difference between
    the four neighbor temperatures and 4 times the current temperature.
    """
    if grid_size < 3:
        raise ValueError("grid_size must be at least 3.")
    if chip_size <= 0.0 or alpha <= 0.0:
        raise ValueError("chip_size and alpha must be positive.")
    if dt <= 0 or total_time <= 0:
        raise ValueError("dt and total_time must be positive.")
    if cooling_rate < 0.0 or boundary_cooling_rate < 0.0:
        raise ValueError("cooling rates must be non-negative.")
    if animation_stride <= 0:
        raise ValueError("animation_stride must be positive.")
    if boundary_condition not in {"dirichlet", "robin"}:
        raise ValueError("boundary_condition must be 'dirichlet' or 'robin'.")
    if checkerboard_perturbation < 0.0:
        raise ValueError("checkerboard_perturbation must be non-negative.")
    if stop_temperature_limit is not None and stop_temperature_limit <= 0.0:
        raise ValueError("stop_temperature_limit must be positive.")

    dx = chip_size / (grid_size - 1)
    r = alpha * dt / (dx * dx)
    if enforce_stability and r > 0.25:
        stable_dt = 0.25 * dx * dx / alpha
        raise ValueError(
            f"Unstable explicit scheme for scenario '{scenario_name}': "
            f"r = {r:.4f} > 0.25. Use dt <= {stable_dt:.6g}."
        )

    steps = int(round(total_time / dt))
    times = np.linspace(0.0, steps * dt, steps + 1)

    u = np.full((grid_size, grid_size), initial_temperature, dtype=float)
    if boundary_condition == "dirichlet":
        apply_dirichlet_boundary(u, boundary_temperature)

    core_mask = create_core_mask(grid_size, core_fraction)
    boundary_mask = create_boundary_mask(grid_size)
    if checkerboard_perturbation > 0.0:
        row_indices, col_indices = np.indices(u.shape)
        checkerboard = np.where((row_indices + col_indices) % 2 == 0, 1.0, -1.0)
        u[~boundary_mask] += checkerboard_perturbation * checkerboard[~boundary_mask]
        if boundary_condition == "dirichlet":
            apply_dirichlet_boundary(u, boundary_temperature)

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
    stop_reason: str | None = None

    for step in range(steps + 1):
        current_time = step * dt
        tmax[step] = float(np.max(u))

        if step in snapshot_indices or stop_reason is not None:
            snapshots.append(u.copy())
            stored_snapshot_times.append(current_time)

        if step % animation_stride == 0 or step == steps or stop_reason is not None:
            animation_frames.append(u.copy())

        if step == steps or stop_reason is not None:
            break

        if boundary_condition == "dirichlet":
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
            apply_dirichlet_boundary(u_new, boundary_temperature)
        else:
            u_new = (
                u
                + r * laplacian_with_insulated_outer_edge(u)
                + dt * q
                - dt * cooling_rate * (u - boundary_temperature)
            )
            u_new[boundary_mask] -= (
                dt
                * boundary_cooling_rate
                * (u[boundary_mask] - boundary_temperature)
            )

        u = u_new

        if not np.all(np.isfinite(u)):
            stop_reason = (
                f"Stopped at t = {(step + 1) * dt:.4f} s because the "
                "temperature field became non-finite."
            )
        elif (
            stop_temperature_limit is not None
            and float(np.max(np.abs(u))) >= stop_temperature_limit
        ):
            stop_reason = (
                f"Stopped at t = {(step + 1) * dt:.4f} s because "
                f"|temperature| exceeded {stop_temperature_limit:g} deg C."
            )

    times = times[: step + 1]
    tmax = tmax[: step + 1]
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
        boundary_condition=boundary_condition,
        boundary_cooling_rate=boundary_cooling_rate,
        stop_reason=stop_reason,
    )
