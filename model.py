from typing import List
import matplotlib.pyplot as plt
import numpy as np
from Agent import VehicleAgent


class Model:
    def __init__(self, num_agents: int, dt: float = 0.1) -> None:
        self.agents: List[VehicleAgent] = []
        self.dt = dt
        self.xs = []
        self.vs = []
        for i in range(num_agents):
            self.agents.append(VehicleAgent(i * 15, 0, b=0.0))
            self.xs.append([])
            self.vs.append([])

    def reset(self) -> None:
        self.__init__(len(self.agents), self.dt)

    def run(self) -> None:
        t = 0
        for _ in range(1000):
            print(t)
            # HACK(Seb): Hardcode the leader to brake at t=50 to emulate Fig 6C
            if np.isclose(t, 50):
                self.agents[-1].current_speed = 0
            for i in range(len(self.agents) - 1):
                self.xs[i].append(self.agents[i].position)
                self.vs[i].append(self.agents[i].current_speed)

                gap = self.agents[i + 1].position - self.agents[i].position
                leader_speed = self.agents[i + 1].current_speed
                leader_acceleration = self.agents[i + 1].acceleration
                self.agents[i].update_state(
                    gap, leader_speed, leader_acceleration, self.dt, 2000
                )

            self.xs[-1].append(self.agents[-1].position)
            self.vs[-1].append(self.agents[-1].current_speed)
            # HACK(Seb): I've got no better idea to let the leader know that it's not following anyone.
            self.agents[-1].update_state(10000000, 100, 100, self.dt, 2000)

            t += self.dt

    def plot(self, stat: str = "position", out_file=None) -> None:
        for i in range(len(self.agents)):
            if stat == "position":
                plt.plot(np.arange(1000) * self.dt, self.xs[i])
            elif stat == "velocity":
                plt.plot(np.arange(1000) * self.dt, self.vs[i])
                # plt.plot(np.arange(999) * self.dt, np.diff(self.xs[i]) / self.dt)
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
