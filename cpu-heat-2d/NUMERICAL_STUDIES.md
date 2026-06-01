# Numerical Studies Added to the Project

This project now includes three additions that make the simulation stronger for a
Scientific Computing presentation.

## 1. Grid and Time Convergence Study

The code runs the same base heat equation setup with different numerical
resolutions:

- Grid convergence: `grid_size = 40, 80, 120`
- Time convergence: `dt = 0.04, 0.02, 0.01`

For each run, the solver records:

- `grid_size`
- `dt`
- `dx`
- stability ratio `r = alpha * dt / dx^2`
- final maximum temperature `Tmax_final`

The results are saved to:

```text
outputs/numerical_studies/convergence_summary.csv
outputs/numerical_studies/grid_convergence.png
outputs/numerical_studies/time_convergence.png
```

This shows how the numerical result changes as the mesh or time step is refined.
In a Scientific Computing report, this is useful because a numerical solution
should not depend too strongly on an arbitrary grid choice.

## 2. Unstable Error Blow-up Demo

The project also includes a runnable unstable demo saved with the same structure
as the main scenarios:

```text
outputs/unstable_error_blowup/
outputs/unstable_error_blowup/unstable_error_blowup_heatmap_snapshots.png
outputs/unstable_error_blowup/unstable_error_blowup_final_heatmap.png
outputs/unstable_error_blowup/unstable_error_blowup_tmax.png
outputs/unstable_error_blowup/unstable_error_blowup_animation.gif
outputs/unstable_error_blowup/unstable_error_blowup_report.txt
```

This scenario intentionally disables the stability guard and uses `r > 1/4`.
A very small checkerboard perturbation is added to the initial condition. This
perturbation represents high-frequency numerical error, and for `r > 1/4` it
grows rapidly instead of being damped. The result is a visible numerical blow-up
in the heatmaps and in the `Tmax(t)` plot.

The normal scenarios still keep the stability guard enabled.

## 3. Stability Guard Experiment

The explicit finite difference method for the 2D heat equation requires:

```text
r <= 1/4
```

The project now includes an intentionally unstable scenario with a large `dt`.
The solver catches it and writes a report instead of running an invalid
simulation:

```text
outputs/numerical_studies/stability_experiment.txt
```

This demonstrates that the implementation checks numerical stability, not just
that it produces images.

## 4. Robin Boundary Cooling

The original model keeps the chip boundary fixed at `25 deg C`, which is a
Dirichlet boundary condition:

```text
u = ambient_temperature on the boundary
```

The new `robin_boundary_cooling` scenario uses a simplified Robin/Newton cooling
boundary. The boundary is no longer fixed directly. Instead, boundary cells lose
heat at a rate proportional to their temperature difference from ambient:

```text
heat_loss = boundary_cooling_rate * (T_boundary - T_ambient)
```

This is closer to the physical idea of convective cooling, where hotter surfaces
lose heat faster to the surrounding environment.

The Robin scenario is saved with the other main scenarios:

```text
outputs/robin_boundary_cooling/
```
