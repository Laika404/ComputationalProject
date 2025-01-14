import enum
from typing import List
import matplotlib.pyplot as plt
import numpy as np
from Agent import VehicleAgent


class Model:
    def __init__(
        self, num_agents: int, timesteps=1000, road_len=2000.0, dt=0.1
    ) -> None:
        self.agents: List[VehicleAgent] = []
        self.dt = dt
        self.timesteps = timesteps
        self.xs = []
        self.vs = []
        self.road_len = road_len
        for i in range(num_agents):
            self.agents.append(VehicleAgent(i * 15, 0, b=0.0))
            self.xs.append([])
            self.vs.append([])

    def reset(self) -> None:
        self.__init__(len(self.agents), self.dt)

    def run(self, periodic=False) -> None:
        t = 0
        for _ in range(self.timesteps):
            # HACK(Seb): Hardcode the leader to brake at t=50 to emulate Fig 6C
            if np.isclose(t, 50) and not periodic:
                self.agents[-1].current_speed = 0

            for i, agent in enumerate(self.agents):
                self.xs[i].append(agent.position)
                self.vs[i].append(agent.current_speed)

            if not periodic:
                for i in range(len(self.agents) - 1):
                    gap = self.agents[i + 1].position - self.agents[i].position
                    leader_speed = self.agents[i + 1].current_speed
                    leader_acceleration = self.agents[i + 1].acceleration
                    self.agents[i].update_state(
                        gap, leader_speed, leader_acceleration, self.dt, None
                    )

                # HACK(Seb): I've got no better idea to let the leader know that it's not following anyone.
                self.agents[-1].update_state(10000000, 100, 100, self.dt, None)
            else:
                for i in range(len(self.agents)):
                    leader = self.agents[(i + 1) % len(self.agents)]
                    gap = leader.position - self.agents[i].position
                    if gap < 0:
                        gap += self.road_len
                    self.agents[i].update_state(
                        gap,
                        leader.current_speed,
                        leader.acceleration,
                        self.dt,
                        self.road_len,
                    )

            t += self.dt

    def plot(self, stat: str = "position", out_file=None) -> None:
        ts = np.arange(len(self.xs[0])) * self.dt
        for i in range(len(self.agents)):
            if stat == "position":
                plt.plot(ts, self.xs[i])
            elif stat == "velocity":
                plt.plot(ts, self.vs[i])
                # plt.plot(ts[:-1], np.diff(self.xs[i]) / self.dt)
            elif stat == "mean_velocity":
                vs = np.vstack(self.vs)
                plt.plot(ts, np.mean(vs, axis=0))
                break
            else:
                raise ValueError(f"Unrecognised statistic '{stat}'")

        if out_file is None:
            plt.show()
        else:
            plt.savefig(out_file)


m = Model(6)
m.run()
m.plot()
m.plot(stat="velocity")

m = Model(20, timesteps=3000)
m.run(periodic=True)
m.plot()
m.plot(stat="velocity")
m.plot(stat="mean_velocity")
