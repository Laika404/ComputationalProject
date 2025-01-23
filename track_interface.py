import numpy as np
from Agent import VehicleAgent


class Track:

    def __init__(self, lane_count = 2, length=2000):
        self.length = length
        self.lanes_count = lane_count
        # most right lane == 0 and is the slowest lane
        self.lanes_list = [[] for _ in range(lane_count)]

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
        for lane in self.lanes_list:
            for vehicle in self.lanes_list:
                vehicle.calculate_next_state()
    
    def update_state(self):
        for lane in self.lanes_list:
            for vehicle in self.lanes_list:
                vehicle.update_state()
    
    # positive count means switching to a lane more to the left
    # lane and position are used to find the current car
    def switch_lane(self, lane, position, count=1 ):
        pass 
    
    # returns the car in front
    # finds the car based on the position argument and returns the closest car in front
    # if two or more cars are on the same position it returns a list of all cars on this position
    def car_in_front(self, lane, position):
        # returns the vehicle in front
        pass

    def car_in_back(self, lane, position):
        # returns the vehicle in the back
        pass
    
    # finds the car closest on the left and right lane of this car
    def closest_cars_sides(self, cur_lane, position):
        # back car is >=
        # returns are syntaxed as
        # dict(lane: tuple(front_car, back_car))
        pass  


bab = Track(lane_count=5)
print(bab.lanes_count)
bab.init_cars(density=100, equal_lanes=False)
print(len(bab.lanes_list[0]))
