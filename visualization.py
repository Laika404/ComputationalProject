import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl

########################################
# PARAMETERS
########################################
CIRCUMFERENCE = 2000.0  # meters
LANE_WIDTH = 10        # meters (example)
NUM_LANES = 1

# Calculate the base radius for the innermost lane
# Circumference = 2 * pi * R  =>  R = circumference / (2*pi)
BASE_RADIUS = CIRCUMFERENCE / (2.0 * np.pi)

# If you have more than one lane, each lane i has radius R_i = BASE_RADIUS + i*LANE_WIDTH
# We'll define a helper function to compute radius given a lane index
def get_lane_radius(lane_index):
    return BASE_RADIUS + lane_index * LANE_WIDTH

########################################
# LOAD CSV DATA
########################################
df = pd.read_csv("data.csv")
# CSV columns expected: car_id, timestep, alpha, lane, speed

# Get unique timesteps in sorted order
timesteps = sorted(df["timestep"].unique())

########################################
# SET UP MATPLOTLIB FIGURE
########################################
fig, ax = plt.subplots()
min_speed = df["speed"].min()
max_speed = df["speed"].max()
cmap = plt.colormaps.get_cmap("coolwarm")
norm = mpl.colors.Normalize(vmin=min_speed, vmax=max_speed)
sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
cbar = fig.colorbar(sm, ax=ax, orientation="vertical", fraction=0.05, pad=0.05)
cbar.set_label("Speed (m/s)")


# For a nice equal aspect ratio (so circle looks circular)
ax.set_aspect("equal", adjustable="box")

# Determine a good bounding box around the circle
# e.g., slightly bigger than BASE_RADIUS + (NUM_LANES-1)*LANE_WIDTH
max_lane = df["lane"].max() if "lane" in df.columns else 0
outer_radius = get_lane_radius(max_lane)
padding = 10  # some extra space
ax.set_xlim(-outer_radius - padding, outer_radius + padding)
ax.set_ylim(-outer_radius - padding, outer_radius + padding)

# Draw each lane as a dashed circle for reference, may need to be hardcoded
# for lane narrowing
theta_vals = np.linspace(0, 2*np.pi, 360)
for lane_i in range(max_lane + 1):
    r_lane = get_lane_radius(lane_i)
    x_lane = r_lane * np.cos(theta_vals)
    y_lane = r_lane * np.sin(theta_vals)
    ax.plot(x_lane, y_lane, "--", color="gray", linewidth=0.5)

# We will use a scatter plot to represent cars
# Initially, it's empty; we'll update it in each frame of the animation
scat = ax.scatter([], [], c="red", s=20, alpha=0.8)

########################################
# HELPER FUNCTIONS
########################################

def alpha_to_xy(alpha, lane):
    """
    Convert arc-length alpha to Cartesian (x, y) for a given lane.
    - alpha in [0, 2000)
    - lane is an integer (0 = innermost lane, 1, 2, etc.)
    """
    # Convert alpha to angle (theta) in radians
    theta = 2.0 * np.pi * (alpha / CIRCUMFERENCE)

    # Get lane radius
    r = get_lane_radius(lane)

    # Convert to (x, y)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

def init():
    """Initialize the background of the animation (nothing to update yet)."""
    return scat,

def update(frame):
    """
    For each frame (which corresponds to a given timestep),
    filter the dataframe to that timestep, convert (alpha, lane) to (x, y),
    and update the scatter plot.
    """
    # Filter data for this timestep
    data_t = df[df["timestep"] == frame]

    # Convert alpha -> (x, y) for each row
    x_vals = []
    y_vals = []
    colors = []

    for _, row in data_t.iterrows():
        x, y = alpha_to_xy(row["alpha"], row["lane"])
        x_vals.append(x)
        y_vals.append(y)

        colors.append(row["speed"])

    # Update scatter: need an Nx2 array for offsets
    scat.set_offsets(np.column_stack((x_vals, y_vals)))

    cmap = plt.cm.get_cmap("coolwarm")
    norm = plt.Normalize(vmin=df["speed"].min(), vmax=df["speed"].max())
    scat.set_color(cmap(norm(colors)))
    return scat,

########################################
# CREATE THE ANIMATION
########################################
ani = animation.FuncAnimation(
    fig,
    update,
    frames=timesteps,
    init_func=init,
    blit=True,
    repeat=True
)

plt.show()

ani.save(filename="pillow_example.gif", writer="pillow")
