rom functools import cmp_to_key
from Agent import VehicleAgent
import numpy as np



# a lane which can contain cars, cars are stored in order
class Lane:
    # used for ordering cars by position in lists. used by function sorted
    def _compare_car_pos(car_a: VehicleAgent, car_b: VehicleAgent):
        if car_a.position < car_b.position:
            return -1
        elif car_a.position > car_b.position:
            return 1
        else:
            return 0
    _car_sort_key = cmp_to_key(_compare_car_pos)
    
    # length is in meters
    def __init__(self, length=2000, circle=True):
        self.length = 2000
        # are in order
        self.car_list: list[VehicleAgent] = []

        self.connection = "self"
        
        # amount of crossings / going beond
        self.crossings = 0

    def add_all_car(self,  car_list):
        self.car_list = sorted(car_list, key=Lane._car_sort_key)

        for car in self.car_list:
            car.track = self

    def add_car(pos):
        pass
    
    def get_gap(self, leader: VehicleAgent, follower: VehicleAgent):
        # gap = leader.position - follower.position - leader.length
        # if (leader.position < follower.position) and ((leader.position != None) or (follower.position != None)):
        #     gap += 2000
        gap = (leader.position - follower.position) % self.length
        # bug if speed difference more than 10 m/s and follower overtakes leader
        if (-200< leader.position - follower.position <0):
            gap = 0
        else:
            gap = max(0, gap - leader.length)

        return gap

    # updates all the cars in the lane, in speed and position
    def update_cars_lane(self):
        amount_cars = len(self.car_list)
        for i in range(amount_cars):
            follower = self.car_list[i]
            leader = self.car_list[(i+1)%amount_cars]
                
            follower.update_next(leader)
        for vehicle in self.car_list:
            vehicle.update_state()
            if (vehicle.position >= self.length):
                vehicle.position = vehicle.position%self.length
                self.crossings +=1

    def get_mean_speed(self):
        return np.mean([vehicle.current_speed for vehicle in self.car_list])

    def remove_all_car(self):
        for car in self.car_list:
            car.track = None
        self.car_list = []
        
    def reset_crossing(self):
        self.crossings = 0
    
    def print_all_gaps(self):
        amount_cars = len(self.car_list)
        for i in range(amount_cars):
            follower = self.car_list[i]
            leader = self.car_list[(i+1)%amount_cars]
            print(self.get_gap(leader, follower))
