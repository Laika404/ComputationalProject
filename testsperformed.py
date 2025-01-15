# case 1: parallele updates, verbazingwekkend genoeg waren de flows nu juist heel laag, hoogste was rond 100
def run(self) -> None:
    for density in self.density_values:
        # N is the number of vehicles
        N = int(density * self.road_length_km)
        initial_positions = np.sort(np.random.uniform(0, self.road_length - (N * 5), N))
        initial_positions += np.arange(N) * 5 # Ensure minimum gaps of 5m by adding vehicle length

        vehicles: List[VehicleAgent] = [
            VehicleAgent(pos, 30) for pos in initial_positions
        ]

        total_crossings = 0

        for t in range(int(self.total_time / self.dt)):
            vehicles.sort(key=lambda vehicle: vehicle.position)

            next_positions = []
            next_speeds = []

            for i, vehicle in enumerate(vehicles):
                leader = vehicles[(i + 1) % N]
                gap = (leader.position - vehicle.position) % self.road_length
                gap = max(0, gap - leader.length)

                v_safe = vehicle.compute_safe_speed(gap, leader.current_speed)
                v_ideal = min(vehicle.max_speed, vehicle.current_speed + vehicle.acceleration * self.dt, v_safe)
                eta = np.random.uniform(0, 1)
                next_speed = max(0, v_ideal - vehicle.b * eta)
                next_position = (vehicle.position + next_speed * self.dt)

                if next_position >= self.road_length:
                    next_position -= self.road_length
                    total_crossings += 1

                next_positions.append(next_position)
                next_speeds.append(next_speed)

            # Update states in parallel
            for i, vehicle in enumerate(vehicles):
                vehicle.current_speed = next_speeds[i]
                vehicle.position = next_positions[i]

        flow = (total_crossings / self.total_time) * 3600
        mean_speed = np.mean([vehicle.current_speed for vehicle in vehicles])

        self.flow_results.append(flow)
        self.speed_results.append(mean_speed)


# case 2: - 2 dingen geprobeerd met de distance, of het misschien daaraan lag
for i, vehicle in enumerate(vehicles):
    leader = vehicles[(i + 1) % N]
    gap = (leader.position - vehicle.position) % self.road_length
    gap = max(0, abs(gap – 2 * leader.length))

for i, vehicle in enumerate(vehicles):
    leader = vehicles[(i + 1) % N]
    gap = (leader.position - vehicle.position) % self.road_length
    gap = max(0, abs(gap - leader.length))

# case 3: 20 runs voor elke density, net als in paper. En scatterplot voor elke run voor elke density, in de paper is de grafiek niet 1 lijn. 
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
        self.density_values = np.linspace(20, 120, 10)
        self.flow_results = []
        self.speed_results = []

    def run(self) -> None:
        for density in self.density_values:
            N = int(density * self.road_length_km)
            initial_positions = np.sort(np.random.uniform(0, self.road_length - (N * 5), N))
            initial_positions += np.arange(N) * 5 # Ensure minimum gaps of 5m by adding vehicle length

            run_flows = [] # Store results for 20 runs, in the paper they also do 20 runs, see macroscopic section
            for run in range(20):
                vehicles = [VehicleAgent(pos, 30) for pos in initial_positions]
                total_crossings = 0

                for t in range(int(self.total_time / self.dt)):
                    vehicles.sort(key=lambda vehicle: vehicle.position)

                    for i, vehicle in enumerate(vehicles):
                        leader = vehicles[(i + 1) % N]
                        gap = abs((leader.position - vehicle.position)) % self.road_length
                        gap = max(0, gap - leader.length)

                        vehicle.update_state(
                            gap=gap,
                            leader_speed=leader.current_speed,
                            leader_acceleration=leader.acceleration,
                            dt=self.dt,
                            # road_length=self.road_length,
                        )

                        if vehicle.position >= self.road_length:
                            vehicle.position -= self.road_length
                            total_crossings += 1

                flow = (total_crossings / self.total_time) * 3600
                run_flows.append(flow) # Save flow for this run

                # print(run_flows)
            self.flow_results.append(run_flows) # Save all runs for this density


    def plot(self, stat: str = "position", out_file=None) -> None:
        if stat == "position":
            for i, run_flows in enumerate(self.flow_results):
                density = self.density_values[i] # Current density value
                for flow in run_flows:
                    plt.scatter([density], [flow], color='gray', alpha=0.5) # Scatter plot for each run at this density

            # the mean flow for each density
            plt.plot(self.density_values, [np.mean(flows) for flows in self.flow_results], color='black', label='Mean Flow')
            plt.xlabel('Density (veh/km)')
            plt.ylabel('Flow (veh/h)')
            plt.legend()

        # deze heb ik niet zoals hierboven gedaan omdat ik eerst met position wilde testen of het wel goed is. 
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

# case 4: - different initial speed initialization
vehicles = [VehicleAgent(pos, 0) for pos in initial_positions]
# en
vehicles = [VehicleAgent(pos, 20) for pos in initial_positions]
# dit veranderde niets

# case 5: - ik dacht misschien kan er wat mis zijn bij de decceleration scenarios:
def decceleration_rate(self, vF, vL, aL, gap, gap_desire):
    # case 1: free flowing case
    if vF > self.desired_speed:
        aF = min((vF - self.desired_speed) / 3, self.a_normal)
        return aF

    # case 2: car-following regime, normal decceleration
    if gap - gap_desire == 0:
        if not vL >= vF:
            aF = (vF**2 - vL**2) / (2*gap)
            return aF

    # case 3: emergency decceleration
    if gap - gap_desire < 0:
        if not vL > vF:
        aF = aL - 0.25 * self.a_normal
        return aF

    # case 4: near-collision decceleration
    if (gap - gap_desire > 0) and (not vL >= vF) and (not gap > 3 * vF) and (not ((gap > 2 * vF) and (gap > 7.5))):
        aF = min(
            aL + ((vF - vL)**2 / (2 * gap)),
            self.a_max
        )
        return aF

    return 0

# Dus ik probeerde hier een aantal permutaties van de scenarios uit, maar ik zag geen verbetering van de flow, nog steeds te hoog. 