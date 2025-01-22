class Track:

    def __init__(self, lane_count = 2, length=2000):
        self.lanes_count = 2
        # most right lane == 0 and is the slowest lane
        self.lanes_list = [[] for _ in range(lane_count)]

    def init_cars(self, density=10):
        pass

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