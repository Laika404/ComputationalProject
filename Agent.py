import numpy as np


# car object that behaves like a car
class VehicleAgent(object):
    def __init__(
        self,
        position,
        current_speed,
        desired_speed=30,
        max_speed=35,
        length=5,
        a_normal=3.05,
        a_max=6.04,
        b=0.2,
        TP=1.2,
    ):
        """
        The parameters of the vehicle agent are:
        - position: the range is [0, 2000> and indicates the position of the vehicle on the lane
        - current speed: the current speed of the vehicle in m/s
        - desired speed: the desired speed of the vehicle, 30 m/s
        - max speed: the maximum speed of the vehicle, 35 m/s
        - length: the length of the vehicle, which is 5m
        - a normal: the normal acceleration, used in specific scenarios (refer to decceleration_rate())
        - a max: the maximum acceleration, used in specific scenarios (refer to decceleration_rate())
        - b: the noise of the model, accounting for the real world environment
        - TP: the time headway the follower prefers to the vehicle in front
        """

        self.position = position
        self.current_speed = current_speed
        self.desired_speed = desired_speed
        self.max_speed = max_speed
        self.length = length
        self.a_normal = a_normal
        self.a_max = a_max
        self.b = b
        self.TP = TP
        self.acceleration = 0

    def compute_decision(self, gap, leader_speed, leader_acceleration):
        """
        The Decision Tree. Returns the decision: accelerate,
        deccelerate or cruise.
        """
        vF = self.current_speed
        vL = leader_speed
        gap_desire = vF * self.TP
        if gap < 6 * vF:
            delta = gap - gap_desire

            if delta > 0:
                if vL >= vF:
                    # accelerate
                    self.acceleration = self.acceleration_rate(vF)

                else:
                    if gap > 3 * vF:
                        # accelerate
                        self.acceleration = self.acceleration_rate(vF)

                    else:
                        if (gap > 2 * vF) and (gap > 7.5):
                            # cruise
                            self.acceleration = 0

                        else:
                            # deccelerate
                            self.acceleration = self.decceleration_rate(
                                vF, vL, leader_acceleration, gap, gap_desire
                            )

            elif delta == 0:
                if vL >= vF:
                    # cruise
                    self.acceleration = 0

                else:
                    # deccelerate
                    self.acceleration = self.decceleration_rate(
                        vF, vL, leader_acceleration, gap, gap_desire
                    )

            elif delta < 0:
                if vL > vF:
                    # cruise
                    self.acceleration = 0

                else:
                    # deccelerate
                    self.acceleration = self.decceleration_rate(
                        vF, vL, leader_acceleration, gap, gap_desire
                    )

        else:
            delta = vF - self.desired_speed

            if delta < 0:
                # accelerate
                self.acceleration = self.acceleration_rate(vF)

            elif delta == 0:
                # cruise
                self.acceleration = 0

            elif delta > 0:
                # deccelerate
                self.acceleration = self.decceleration_rate(
                    vF, vL, leader_acceleration, gap, gap_desire
                )

    def decceleration_rate(self, vF, vL, aL, gap, gap_desire):
        # case 1: free flowing case
        if vF > self.desired_speed:
            aF = min((vF - self.desired_speed) / 3, self.a_normal)
            return aF

        # case 2: car-following regime, normal decceleration
        if gap - gap_desire == 0:
            if not vL >= vF:
                aF = (vF**2 - vL**2) / (2 * gap)
                return aF

        # case 3: emergency decceleration
        if gap - gap_desire < 0:
            if not vL > vF:
                aF = aL - 0.25 * self.a_normal
                return aF

        # case 4: near-collision decceleration
        if (
            (gap - gap_desire > 0)
            and (not vL >= vF)
            and (not gap > 3 * vF)
            and (not ((gap > 2 * vF) and (gap > 7.5)))
        ):
            aF = min(aL + ((vF - vL) ** 2 / (2 * gap)), self.a_max)
            return aF

        return 0

    def acceleration_rate(self, vF):
        if vF <= 12.19:
            aF = 1.1

        elif vF > 12.19:
            aF = 0.37

        return aF

    def compute_safe_speed(self, gap, leader_speed):
        reaction_time = 1
        v_safe = leader_speed + (
            (gap - leader_speed * reaction_time)
            / (
                reaction_time
                + ((self.current_speed + leader_speed) / (2 * self.a_max))
            )
        )
        return v_safe

    def update_state(self, gap, leader_speed, leader_acceleration, dt):
        """
        Updates the state of the follower (current vehicle), which
        depends on the speed and acceleration of the leader (car in front),
        and the gap between them.
        """

        self.compute_decision(gap, leader_speed, leader_acceleration)
        v_safe = self.compute_safe_speed(gap, leader_speed)
        v_ideal = min(
            self.max_speed, self.current_speed + self.acceleration * dt, v_safe
        )
        eta = np.random.rand()
        self.current_speed = max(0, v_ideal - self.b * eta)
        self.position += self.current_speed * dt
