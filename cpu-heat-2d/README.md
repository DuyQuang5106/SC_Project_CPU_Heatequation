# 2D CPU Heat Simulation with Explicit Finite Differences

This project simulates heat diffusion on a simplified two-dimensional CPU chip.
It models a square chip with a heat-generating CPU core near the center and
cooling at the outer boundary. The numerical method is an explicit finite
difference scheme for the 2D heat equation with a source term.

The project uses:

- NumPy for array-based numerical computation.
- Matplotlib for plots, heatmaps, and animations.
- Pillow through Matplotlib for saving GIF animations.

## Project Goals

The main goals of this project are to:

- Simulate how heat spreads from a CPU core through a 2D chip surface.
- Compare different physical and numerical scenarios, such as CPU load,
  cooling strength, thermal diffusivity, and boundary models.
- Visualize the temperature field with heatmaps, animations, and maximum
  temperature curves.
- Demonstrate an important stability condition of the explicit finite
  difference method.
- Run simple grid and time convergence studies to show how numerical choices
  affect the final result.

## Physical Model

The CPU is represented as a square 2D plate. The central core region generates
heat continuously, while the surrounding chip material conducts that heat away.

The temperature field is written as:

```text
u(x, y, t)
```

where `u` is the temperature in degrees Celsius at position `(x, y)` and time
`t`.

Important quantities:

- `alpha`: thermal diffusivity. A larger value means heat spreads faster.
- `Q(x, y)`: heat source term. It is nonzero in the CPU core and zero outside
  the core.
- `initial_temperature`: the starting temperature of the chip.
- `boundary_temperature`: the ambient or cooling temperature.
- `cooling_rate`: an optional internal cooling term that pulls temperatures
  toward the boundary temperature.
- `boundary_condition`: either fixed-temperature Dirichlet cooling or simplified
  Robin/Newton boundary cooling.

## Mathematical Model

The simulation solves the 2D heat equation with a source term:

```text
du/dt = alpha * (d2u/dx2 + d2u/dy2) + Q(x, y)
```

The initial condition is:

```text
u(x, y, 0) = initial_temperature
```

For the default Dirichlet boundary condition, the four chip edges are fixed at:

```text
u = boundary_temperature
```

For the Robin boundary scenario, the boundary is not fixed directly. Instead,
boundary cells lose heat at a rate proportional to their temperature difference
from the ambient temperature:

```text
heat_loss = boundary_cooling_rate * (T_boundary - T_ambient)
```

This approximates convective cooling, where hotter surfaces lose heat faster to
the surrounding environment.

## Numerical Method

The chip is discretized into a square `N x N` grid. The temperature at grid point
`(i, j)` is stored as:

```text
U[i, j]
```

The project uses equal grid spacing in both directions:

```text
dx = dy = chip_size / (grid_size - 1)
```

The explicit finite difference update for an interior cell is:

```text
U_new[i, j] =
    U[i, j]
    + r * (U[i+1, j] + U[i-1, j] + U[i, j+1] + U[i, j-1] - 4U[i, j])
    + dt * Q[i, j]
```

where:

```text
r = alpha * dt / dx^2
```

When internal cooling is enabled, the update also includes:

```text
- dt * cooling_rate * (U[i, j] - boundary_temperature)
```

This term pulls the temperature toward the ambient cooling temperature.

## Stability Condition

For the explicit finite difference method applied to the 2D heat equation, the
stability ratio must satisfy:

```text
r <= 1/4
```

or equivalently:

```text
dt <= dx^2 / (4 * alpha)
```

If `r` is too large, the numerical solution can oscillate or blow up. This is a
numerical instability, not a physically meaningful temperature increase.

The solver checks this condition by default. If a scenario is unstable, it raises
an error and reports the maximum stable `dt`. The project also includes an
intentional unstable blow-up demo where the stability guard is disabled to show
what instability looks like.

## Project Structure

```text
cpu-heat-2d/
+-- main.py
+-- solver.py
+-- scenarios.py
+-- visualization.py
+-- NUMERICAL_STUDIES.md
+-- README.md
+-- outputs/
```

File roles:

- `main.py`: runs all scenarios, saves plots, writes reports, and launches the
  numerical studies.
- `solver.py`: contains the heat equation solver, boundary condition handling,
  stability checks, and simulation result data structure.
- `scenarios.py`: defines all simulation parameter sets.
- `visualization.py`: creates heatmap snapshots, final heatmaps, `Tmax(t)`
  plots, scenario comparison plots, convergence plots, and GIF animations.
- `NUMERICAL_STUDIES.md`: documents the added convergence and stability studies.
- `outputs/`: stores generated PNG images, GIF animations, CSV summaries, and
  text reports.

## Main Scenarios

The scenarios are defined in `scenarios.py`.

- `low_load`: lower CPU heat generation.
- `high_load`: higher CPU heat generation.
- `weak_cooling`: small internal cooling rate.
- `strong_cooling`: stronger internal cooling rate.
- `low_alpha`: lower thermal diffusivity, so heat spreads more slowly.
- `high_alpha`: higher thermal diffusivity, so heat spreads more quickly.
- `robin_boundary_cooling`: uses a Robin/Newton cooling boundary instead of
  fixed-temperature edges.

The project also includes:

- `unstable_error_blowup`: an intentionally unstable run with `r > 1/4`,
  disabled stability enforcement, and a tiny checkerboard perturbation to make
  numerical error growth visible.
- Grid convergence cases with `grid_size = 40, 80, 120`.
- Time convergence cases with `dt = 0.04, 0.02, 0.01`.
- A stability guard experiment that intentionally uses an unstable time step and
  confirms that the solver rejects it.

## Requirements

Use Python 3.10 or newer. The code uses modern type hints such as `list[dict]`
and `str | None`.

Install dependencies:

```bash
pip install numpy matplotlib pillow
```

Optional but recommended: create a virtual environment first.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install numpy matplotlib pillow
```

On macOS or Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

## How to Run

From the repository root:

```bash
cd cpu-heat-2d
python main.py
```

The script runs every main scenario, the unstable blow-up demo, and the
numerical studies. Generated files are saved under `outputs/`.

## Generated Outputs

After running the project, the output folder contains files similar to:

```text
outputs/
+-- comparison_tmax.png
+-- low_load/
+-- high_load/
+-- weak_cooling/
+-- strong_cooling/
+-- low_alpha/
+-- high_alpha/
+-- robin_boundary_cooling/
+-- unstable_error_blowup/
+-- numerical_studies/
```

Each main scenario folder contains:

- Heatmap snapshots at selected times.
- A final heatmap.
- A GIF animation of the temperature field.
- A `Tmax(t)` plot showing the maximum chip temperature over time.

The comparison plot is saved as:

```text
outputs/comparison_tmax.png
```

The unstable blow-up demo saves:

```text
outputs/unstable_error_blowup/unstable_error_blowup_heatmap_snapshots.png
outputs/unstable_error_blowup/unstable_error_blowup_final_heatmap.png
outputs/unstable_error_blowup/unstable_error_blowup_tmax.png
outputs/unstable_error_blowup/unstable_error_blowup_animation.gif
outputs/unstable_error_blowup/unstable_error_blowup_report.txt
```

The numerical studies save:

```text
outputs/numerical_studies/convergence_summary.csv
outputs/numerical_studies/grid_convergence.png
outputs/numerical_studies/time_convergence.png
outputs/numerical_studies/stability_experiment.txt
```

## How to Change Simulation Parameters

Edit `scenarios.py` to change the simulation setup.

Common parameters:

- `grid_size`: number of grid points in each direction. Higher values give more
  detail but require more computation.
- `chip_size`: physical size of the square chip domain.
- `alpha`: thermal diffusivity.
- `q_strength`: heat generated by the CPU core.
- `core_fraction`: relative size of the square core region.
- `dt`: time step.
- `total_time`: total simulated time.
- `initial_temperature`: starting chip temperature.
- `boundary_temperature`: cooling or ambient temperature.
- `cooling_rate`: internal cooling strength.
- `boundary_condition`: `"dirichlet"` or `"robin"`.
- `boundary_cooling_rate`: cooling strength for the Robin boundary condition.
- `snapshot_times`: times where heatmap snapshots are saved.
- `animation_stride`: interval, in time steps, between saved animation frames.

When changing `grid_size`, `alpha`, or `dt`, always check the stability ratio:

```text
r = alpha * dt / dx^2
```

For stable explicit simulations, keep:

```text
r <= 0.25
```

## Code Workflow

The main execution flow is:

1. `main.py` loads scenario dictionaries from `scenarios.py`.
2. Each scenario is passed to `solve_heat_equation()` in `solver.py`.
3. The solver builds the temperature grid `U`, the core heat source matrix `Q`,
   and the core mask.
4. The solver advances the temperature field in time using the explicit finite
   difference formula.
5. Selected snapshots, animation frames, and maximum temperature values are
   stored in a `SimulationResult`.
6. `visualization.py` saves heatmaps, animations, and `Tmax(t)` plots.
7. `main.py` saves comparison plots, convergence summaries, and stability
   experiment reports.

## Interpreting Results

Heatmaps show the spatial temperature distribution across the chip. Brighter or
warmer colors represent higher temperatures. The hottest region is usually the
CPU core because that is where heat is generated.

The `Tmax(t)` plot shows the maximum temperature on the chip over time. Higher
CPU load usually increases `Tmax` faster and leads to a higher final
temperature. Stronger cooling lowers `Tmax`. Higher `alpha` spreads heat more
quickly, which can reduce heat concentration near the core but warms the
surrounding area faster.

The convergence plots show whether the final maximum temperature changes
significantly when the grid or time step is refined. Smaller changes indicate a
more reliable numerical result.

The unstable blow-up demo shows why the condition `r <= 1/4` matters. When this
condition is violated, small numerical errors can grow rapidly and dominate the
simulation.
