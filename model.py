from typing import List
import matplotlib.pyplot as plt
import numpy as np
from Agent import VehicleAgent
from Track import Lane
import copy
import csv

max_speed = 35
desired_speed = 30
TP = 1.2
a_normal = 3.05
a_max = 6.04
b = 0.2


class Model(object):
    
    static_param = {"max_speed": 35, "desired_speed": 30, "TP": 1.2,
                  "a_normal": 3.05, "a_max": 6.04, "b": 0.2}


    
    
    # initialize the model
    # car_spread = ("even", "random")
    # init_speed_var = [0, 1] the percentage
    def __init__(self, dt: float = 1.0, max_time: int = 2000, road_length: int = 2000, density = 10,  car_spread = "random", init_speed_var = 0.2, param = {}, var_param = {}) -> None:
        
        # define a subclass with parameters specific to this simulation
        class Agent(VehicleAgent):
            dt = 1
        self.Agent = Agent

        # simulation parameters
        self.dt = dt
        self.Agent.dt = dt      
        self.road_length = road_length
        self.density = density
        self.car_spread = car_spread
        self.init_speed_var = init_speed_var

        self.cur_time = None
        self.cur_step = None
        self.max_time = max_time
        
        # parameters for the car
        self.param = None
        # do parameters vary
        self.var_param = None
        self.new_parameters(param)

        # agent initializing
        self.agent_list = None

        # track initialization
        self.track = Lane()
        
        
        self.time_data = []
        self.cros_data = []
        self.mean_speed_data = []
        

    # gives the model new parameters. Changes self.param 
    def new_parameters(self, param: dict, var_param: dict[bool]={}) -> None:
        new_param = {}
        for key in Model.static_param.keys():
            if (key in param):
                new_param[key] = param[key]
            else:
                if (self.param == None):
                    new_param[key] = Model.static_param[key]
                else:
                    new_param[key] = self.param[key]
        
        new_var_param = {}
        for key in Model.static_param.keys():
            if (key in var_param):
                new_var_param[key] = var_param[key]
            else:
                if (self.var_param == None):
                    new_var_param[key] = False
                else:
                    new_var_param[key] = self.var_param[key]
        
        self.param = new_param
        self.var_param = new_var_param
    
    # a single step
    def step(self):
        self.track.update_cars_lane()

        self.cur_step += 1
        self.cur_time += self.dt

        # new data
        self.time_data.append(self.cur_time)
        self.cros_data.append(self.track.crossings)
        self.mean_speed_data.append(self.track.get_mean_speed())
        

    def mult_step(self, amount):
        for i in range(amount):
            self.step()

    def run_sim(self):
        self.init_sim()
        while True:
            self.step()
            if (self.cur_time>=self.max_time):
                break
        

    def init_sim(self, new_agents = True):
        # reset track if needed
        self.track.remove_all_car()
        self.track.reset_crossing()
        # amount of cars based on density
        N = int(self.density*(self.road_length/1000))
        print(N)

        # new agents only will be added if
        if new_agents:
            self.init_agents(N)
        
        # initialize different speeds
        # init_speeds = np.random.uniform(self.param["desired_speed"]*(1-self.init_speed_var),
        #                   self.param["desired_speed"]*(1+self.init_speed_var), N)
        init_speeds = np.random.uniform(0, 35, N)

        # initialize positions, spread based on parameters
        if self.car_spread == "even":
            init_pos = np.linspace(0, self.road_length, N)
        elif self.car_spread == "random":
            init_pos = np.sort(np.random.uniform(0, self.road_length - (N * 5), N))
            init_pos += np.arange(N) * 5  # Ensure minimum gaps of 5m by adding vehicle length

        # add speed and position data to the agents
        for i in range(N):
            agent = self.agent_list[i]
            agent.current_speed =init_speeds[i]
            agent.position = init_pos[i]

        # bind cars to the track
        self.track.add_all_car(self.agent_list)

        self.cur_step = 0
        self.cur_time = 0

        # reset data
        self.time_data = []
        self.cros_data = []
        self.mean_speed_data = []
        # add data for step 0
        self.time_data.append(self.cur_time)
        self.cros_data.append(self.track.crossings)
        self.mean_speed_data.append(self.track.get_mean_speed())

    
    # the function makes new agents
    def init_agents(self, amount) -> List:
        self.agent_list = [self.Agent() for i in range(amount)]

        # set agent parameters
        for key in self.param.keys():
            value = self.param[key]
            if self.var_param[key]:
                value_list = np.random.normal(value, value*0.1, amount)
            else:
                value_list = np.full(amount, value)
            for i in range(amount):
                self.agent_list[i].change_parameter(key, value_list[i])
    
    def get_final_data(self):
        return {"time": self.time_data[-1], "cross": self.cros_data[-1], "mean_speed": self.mean_speed_data[-1]}

    def get_all_data(self):
        return {"time": copy.copy(self.time_data), "cross": copy.copy(self.cros_data), "mean_speed": copy.copy(self.mean_speed_data)}

    def get_all_agent_data(self, filename: str):
        
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["id","timestep","alpha","lane","speed"])
            car_id = 0
            for agent in self.agent_list:
                print(car_id)
                for i in range(len(self.time_data)):
                    writer.writerow([car_id, int(self.time_data[i]), agent.pos_data[i], 0, agent.speed_data[i]])
                if (car_id == 1111):
                    break
                car_id +=1
