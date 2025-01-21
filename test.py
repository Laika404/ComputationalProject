import model
import numpy as np
import matplotlib.pyplot as plt


def plot(density_values, speed_results, out_file=None) -> None:
    plt.plot(density_values, speed_results)
    plt.xlabel('density (veh/km)')
    plt.ylabel('mean speed (m/s)')

    if out_file is None:
        plt.show()
    else:
        plt.savefig(out_file)

my_model = model.Model()

# density test
density_values = np.linspace(0, 120, 10)
flow_results = []
speed_results = []
for density in density_values:
    my_model.density = density
    print(density)
    my_model.run_sim()
    # print([float(car.position) for car in my_model.track.car_list])
    # my_model.track.print_all_gaps()
    # my_model.get_all_agent_data("floppie.csv")
    # print(my_model.get_all_data()["mean_speed"])
    final_data = my_model.get_final_data()
    speed_results.append(final_data["mean_speed"])
    flow_results.append(density)

plot(flow_results, speed_results)
