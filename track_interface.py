import numpy as np
from Agent import VehicleAgent


class Track:

    def __init__(self, lane_count = 2, length=2000, dt=1.0):
        self.lanes_count = 2
        # Rightmost lane has index 0 and is the slow lane.
        self.lanes_list = [[] for _ in range(lane_count)]
        self.length = length
        self.dt = dt

    def init_cars(self, density=10, equal_lanes = False):
        N_cars = int((self.length/1000)*density)
        if equal_lanes:
            split_points = np.linspace(0, N_cars, self.lanes_count+1)[1:-1]
        else:
            split_points = np.sort(np.random.uniform(0, N_cars, self.lanes_count - 1))

        try:
            split_points = int(split_points)
        except:
            split_points = split_points.astype(int)

        past_amount = 0
        lane = 0
        for total in split_points:
            self.lanes_list[lane] = self.populate_lane(total - past_amount)
            past_amount = total
            lane += 1

    def populate_lane(self, N):
        print(N)
        initial_positions = np.sort(np.random.uniform(0, self.length - (N * 5), N))
        initial_positions += np.arange(N) * 5  # Ensure minimum gaps of 5m by adding vehicle length

        initial_speeds = np.random.uniform(0, 35, N)
        vehicle_list = [VehicleAgent(initial_positions[i], initial_speeds[i]) for i in range(N)]
        return vehicle_list

    def calculate_next_state(self):
        for i, lane in enumerate(self.lanes_list):
            for vehicle in lane:
                leader = self.car_in_front(i, vehicle.position)
                gap = (leader.position - vehicle.position) % self.length
                vehicle.calculate_next_state(
                    gap,
                    leader.current_speed,
                    leader.acceleration,
                    self.dt,
                )

    def update_state(self):
        for lane in self.lanes_list:
            for vehicle in self.lanes_list:
                vehicle.update_state(self.dt)

    def switch_lane(self, lane, position, count=0):
        """
        Uses lane and position to find the current car and moves it ``count`` lanes.
        Positive values for ``count`` move it to the right.
        """
        if count == 0:
            return

    def car_in_front(self, lane, position):
        """
        Returns the car in front of the one at a certain position in the lane,
        or ``None`` if the lane is empty.
        """
        if len(self.lanes_list[lane]) == 0:
            return None
        return min(veh for veh in self.lanes_list[lane] if veh.position > position)

    def car_in_back(self, lane, position):
        """
        Returns the car behind the one at a certain position in the lane,
        or ``None`` if the lane is empty.
        """
        if len(self.lanes_list[lane]) == 0:
            return None
        return max(veh for veh in self.lanes_list[lane] if veh.position < position)

    def closest_cars_sides(self, cur_lane, position):
        """
        Returns the closest cars in the lanes to the left and right of this car.
        Example output for ``self.closest_cars_sides(0, 100)``: ::

            {
                -1: None,  # There is not lane to the the left of lane 0.
                1: (vehicle_in_front, vehicle_behind),
            }
        """
        left_lane, right_lane = cur_lane - 1, cur_lane + 1
        if right_lane <= 0:
            right = (self.car_in_front(right_lane, position),
                     self.car_in_back(right_lane, position))
        else:
            right = None

        if left_lane > self.lanes_count:
            left = (self.car_in_front(left_lane, position),
                     self.car_in_back(left_lane, position))
        else:
            left = None

        return {
            left_lane: left,
            right_lane: right,
        }
