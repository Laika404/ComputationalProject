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
        self.density_values = np.linspace(0, 140, 10)
        self.flow_results = []
        self.speed_results = []

    def run(self) -> None:
        for density in self.density_values:
            # N is amount of vehicles
            N = int(density * self.road_length_km)
            initial_positions = np.sort(np.random.uniform(0, self.road_length, N))
            print(initial_positions)
            
            vehicles: List[VehicleAgent] = [
                VehicleAgent(pos, 30) for pos in initial_positions
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
                        road_length=self.road_length
                    )

                    if vehicle.position >= self.road_length:
                        vehicle.position -= self.road_length
                        total_crossings += 1

            flow = (total_crossings / self.total_time) * 3600
            mean_speed = np.mean([vehicle.current_speed for vehicle in vehicles])
            
            self.flow_results.append(flow)
            self.speed_results.append(mean_speed)
            
    def plot(self, stat: str = "position", out_file=None) -> None:
        if stat == "position":
            plt.plot(self.density_values, self.flow_results)
            plt.xlabel('density (veh/km)')
            plt.ylabel('flow (veh/h)')

        elif stat == "velocity":
            plt.plot(self.density_values, self.speed_results)
            plt.xlabel('density (veh/km)')
            plt.ylabel('mean speed (m/s)')

        else:
            raise ValueError(f"Unrecognised statistic '{stat}'")

        if out_file is None:
            plt.show()
        else:
            plt.savefig(out_file)


m = Model()
m.run()
m.plot(stat="position")
