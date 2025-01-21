import numpy as np
import matplotlib.pyplot as plt

# car object that behaves like a car
class VehicleAgent(object):

    dt = None

    # dictionary used for optimization
    enum_param = {"max_speed": 0, "desired_speed": 1, "TP": 2,
                  "a_normal": 3, "a_max": 4, "b":5}
    
    def __init__(self, track=None, position=None, current_speed=None, desired_speed=30, max_speed=35, length=5, a_normal=3.05, a_max=6.04, b=0.2, TP=1.2):
        # is of class Lane
        self.track = track
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

        # used for parallel updates
        self.next_speed = None
        self.next_position = None

        self.pos_data = [0]
        self.speed_data = [0]


    def change_parameter(self, param: str, param_val):
        param_number = self.__class__.enum_param[param]
        # change certain parameter
        match param_number:
            case 0:
                self.max_speed = param_val
            case 1:
                self.desired_speed = param_val
            case 2:
                self.TP = param_val
            case 3:
                self.a_normal = param_val
            case 4:
                self.a_max = param_val
            case 5:
                self.b = param_val


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
                            self.acceleration = self.decceleration_rate(vF, vL, leader_acceleration, gap, gap_desire)

            elif delta == 0:
                if vL >= vF:
                    # cruise
                    self.acceleration = 0

                else:
                    # deccelerate
                    self.acceleration = self.decceleration_rate(vF, vL, leader_acceleration, gap, gap_desire)

            elif delta < 0:
                if vL > vF:
                    # cruise
                    self.acceleration = 0

                else:
                    # deccelerate
                    self.acceleration = self.decceleration_rate(vF, vL, leader_acceleration, gap, gap_desire)

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
                self.acceleration = self.decceleration_rate(vF, vL, leader_acceleration, gap, gap_desire)


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


    def acceleration_rate(self, vF):
        if vF <= 12.19:
            aF = 1.1

        elif vF > 12.19:
            aF = 0.37

        return aF

    def compute_safe_speed(self, gap, leader_speed):
        reaction_time = 1
        v_safe = leader_speed + ((gap - leader_speed*reaction_time) / (reaction_time + ((self.current_speed + leader_speed) / (2 * self.a_max))))
        return v_safe

    def update_next(self, leader):
        leader_speed = leader.current_speed
        leader_acceleration = leader.acceleration
        gap = self.track.get_gap(leader, self)

        self.compute_decision(gap, leader_speed, leader_acceleration)
        v_safe = self.compute_safe_speed(gap, leader_speed)
        v_ideal = min(self.max_speed, self.current_speed + self.acceleration * self.__class__.dt, v_safe)
        eta = np.random.uniform(0,1)
        
        self.next_speed = max(0, v_ideal - self.b * eta)
        self.next_position = self.position + self.current_speed * self.__class__.dt
    
    def update_state(self):
        self.current_speed = self.next_speed
        self.position = self.next_position

        self.pos_data.append(self.position)
        self.speed_data.append(self.current_speed)
