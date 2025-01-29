import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl

########################################
# GLOBAL PARAMETERS
########################################
CIRCUMFERENCE = 2000.0  # meters
LANE_WIDTH = 10         # meters (example)
NUM_LANES = 1

# Calculate the base radius for the innermost lane
BASE_RADIUS = CIRCUMFERENCE / (2.0 * np.pi)


def get_lane_radius(lane_index):
    """
    Return the radius of a given lane (0-indexed) based on the innermost lane's radius.
    """
    return BASE_RADIUS + lane_index * LANE_WIDTH


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


def load_data(csv_path):
    """
    Load the CSV data into a Pandas DataFrame and sort timesteps.
    Expected CSV columns: car_id, timestep, alpha, lane, speed
    Returns:
      df: The entire DataFrame
      timesteps: Sorted list of unique timesteps
    """
    df = pd.read_csv(csv_path)
    timesteps = sorted(df["timestep"].unique())
    return df, timesteps


def setup_figure(df):
    """
    Create and return a matplotlib figure and axes with a colorbar
    showing the speed colormap. Also draw the lane circles.
    """
    fig, ax = plt.subplots()

    # Create colormap based on speed
    min_speed = df["speed"].min()
    max_speed = df["speed"].max()
    cmap = plt.colormaps.get_cmap("coolwarm")
    norm = mpl.colors.Normalize(vmin=min_speed, vmax=max_speed)
    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical", fraction=0.05, pad=0.05)
    cbar.set_label("Speed (m/s)")

    # Keep aspect ratio to make circles look circular
    ax.set_aspect("equal", adjustable="box")

    # Determine bounding box for the axis
    max_lane = df["lane"].max() if "lane" in df.columns else 0
    outer_radius = get_lane_radius(max_lane)
    padding = 10
    ax.set_xlim(-outer_radius - padding, outer_radius + padding)
    ax.set_ylim(-outer_radius - padding, outer_radius + padding)

    # Draw lane circles
    theta_vals = np.linspace(0, 2 * np.pi, 360)
    for lane_i in range(max_lane + 1):
        r_lane = get_lane_radius(lane_i)
        x_lane = r_lane * np.cos(theta_vals)
        y_lane = r_lane * np.sin(theta_vals)
        ax.plot(x_lane, y_lane, "--", color="gray", linewidth=0.5)

    return fig, ax


def init_animation():
    """
    Initialize the scatter plot (empty) for FuncAnimation.
    Returns the scatter object (Artists) that will be updated.
    """
    scat = plt.scatter([], [], c="red", s=20, alpha=0.8)
    return (scat,)


def update_animation(frame, df, scat):
    """
    For each frame (timestep):
      1) Filter data for this timestep.
      2) Convert (alpha, lane) to (x, y).
      3) Update scatter plot with new positions and color based on speed.
    """
    data_t = df[df["timestep"] == frame]

    x_vals = []
    y_vals = []
    colors = []

    for _, row in data_t.iterrows():
        x, y = alpha_to_xy(row["alpha"], row["lane"])
        x_vals.append(x)
        y_vals.append(y)
        colors.append(row["speed"])

    scat_obj = scat[0]  # Because scat is a tuple of artists
    scat_obj.set_offsets(np.column_stack((x_vals, y_vals)))

    # Update colors
    cmap = plt.cm.get_cmap("coolwarm")
    norm = plt.Normalize(vmin=df["speed"].min(), vmax=df["speed"].max())
    scat_obj.set_color(cmap(norm(colors)))

    return (scat_obj,)


def main():
    """
    Main function to:
      1) Parse command-line arguments.
      2) Load CSV data.
      3) Create figure and animation.
      4) Save animation to file.
    """
    if len(sys.argv) != 3:
        print("Usage: python circular_animation.py <data_file.csv> <output.gif>")
        sys.exit(1)

    data_file = sys.argv[1]
    output_file = sys.argv[2]

    # 1) Load data
    df, timesteps = load_data(data_file)

    # 2) Create figure
    fig, ax = setup_figure(df)

    # 3) Create scatter (empty) and set up animation
    scat = plt.scatter([], [], c="red", s=20, alpha=0.8)  # or use init_animation()
    ani = animation.FuncAnimation(
        fig,
        update_animation,
        fargs=(df, (scat,)),
        frames=timesteps,
        init_func=init_animation,
        blit=True,
        repeat=True
    )

    # 4) Save animation
    ani.save(filename=output_file, writer="pillow")
    print(f"Animation saved to {output_file}")
    plt.show()


if __name__ == "__main__":
    main()
