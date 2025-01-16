from typing import List
import matplotlib.pyplot as plt
import numpy as np
from Agent import VehicleAgent


class Model(object):
    def __init__(self, dt: float = 1.0, total_time: int = 2000, road_length: int = 2000) -> None:
        self.dt = dt
        self.total_time = total_time
        self.road_length = road_length
        self.road_length_km = self.road_length / 1000
        self.density_values = np.linspace(0, 120, 10)
        self.total_runs = 20 # In the paper they also did 20 runs for each density
        self.flow_results = [[] for _ in range(self.total_runs)]
        self.speed_results = [[] for _ in range(self.total_runs)]


    def run(self, idx) -> None:
        for density in self.density_values:
            # N is amount of vehicles
            N = int(density * self.road_length_km)
            initial_positions = np.sort(np.random.uniform(0, self.road_length - (N * 5), N))
            initial_positions += np.arange(N) * 5  # Ensure minimum gaps of 5m by adding vehicle length
            
            vehicles: List[VehicleAgent] = [
                VehicleAgent(pos, np.random.uniform(0,35)) for pos in initial_positions
            ]
            
            total_crossings = 0

            for t in range(int(self.total_time / self.dt)):
                vehicles.sort(key = lambda vehicle: vehicle.position)

                for i, vehicle in enumerate(vehicles):
                    leader = vehicles[(i + 1) % N]
                    gap = (leader.position - vehicle.position) % self.road_length
                    gap = max(0, gap - leader.length)

                    vehicle.update_state(
                        gap=gap,
                        leader_speed=leader.current_speed,
                        leader_acceleration=leader.acceleration,
                        dt=self.dt,
                    )

                    if vehicle.position >= self.road_length:
                        vehicle.position -= self.road_length
                        total_crossings += 1

            flow = total_crossings
            mean_speed = np.mean([vehicle.current_speed for vehicle in vehicles])
            
            self.flow_results[idx].append(flow)
            self.speed_results[idx].append(mean_speed)
            
            
    def plot(self, stat: str = "position", out_file=None) -> None:
        if stat == "position":
            for idx in range(self.total_runs): # Run the simulation 20 times
                self.run(idx)
            
                # Scatter plot for current run
                plt.scatter(self.density_values, self.flow_results[idx], alpha=0.5, color='gray')
        
            # average flow
            avg_flow = np.mean(self.flow_results, axis=0) if isinstance(self.flow_results[0], list) else self.flow_results
            plt.plot(self.density_values, avg_flow, color='black', label='Mean Flow')
            plt.xlabel('Density (veh/km)')
            plt.ylabel('Flow (veh/h)')
            plt.title('The relationship between flow and density')
            plt.legend()

        elif stat == "velocity":
            for idx in range(20): # Run the simulation 20 times
                self.run(idx)
            
                # Scatter plot for current run
                plt.scatter(self.density_values, self.speed_results[idx], alpha=0.5, color='gray')
        
            # average speed
            avg_speed = np.mean(self.speed_results, axis=0) if isinstance(self.speed_results[0], list) else self.speed_results
            plt.plot(self.density_values, avg_speed, color='black', label='Mean Speed')
            plt.xlabel('Density (veh/km)')
            plt.ylabel('Mean Speed (m/s)')
            plt.title('The relationship between mean-speed and density')
            plt.legend()

        else:
            raise ValueError(f"Unrecognised statistic '{stat}'")

        if out_file is None:
            plt.show()
        else:
            plt.savefig(out_file)


model = Model()
model.plot(stat="velocity")