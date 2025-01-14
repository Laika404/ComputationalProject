import numpy as np
from Agent import Agent

# average values
v_max = 0
v_desire = 0
T_p =0
a_normal = 0
a_max = 0
b = 0

# agents represented as numpy arrays?

# todo add data save methods

class Simulation:

    def __init__(self, agent_count=100, track_length_m=2000, car_length = 5, step_time = 0.1,
                 v_max=v_max, v_desire=v_desire, T_p=T_p, a_normal=a_normal, a_max =a_max, b_noise=b,
                 vary_par_list = [False, False, False, False, False]):
        
        # agent simulation parameters
        self.v_max = v_max
        self.v_desire = v_desire
        self.T_p = T_p
        self.a_normal = a_normal
        self.a_max = a_max
        self.b_noise = b_noise

        self.v_max_var = vary_par_list[0]
        self.v_desire_var = vary_par_list[1]
        self.T_p_var = vary_par_list[2]
        self.a_normal_var = vary_par_list[3]
        self.a_max_var = vary_par_list[4]
        
        # environment simulation parameter
        self.cur_step = 0
        self.agent_count = 100
        # in seconds
        self.step_time = 0.1
        Agent.time_size = 0.1
        # in meters
        self.track_length = 2000
        Agent.track_length = 2000
        self.car_length = 5

        # agent initialization
        self.agent_list = self.agent_init()
        self.agent_list_ordered = self.agent_pos_init()
    
    def agent_init(self):
        agent_list = [Agent() for i in range(self.agent_count)]
        for ag in agent_list:
            ag.v_max = self.v_max
            ag.v_desire = self.v_desire
            ag.T_p = self.T_p
            ag.a_normal = self.a_normal
            ag.a_max = self.a_max
            
            # if parameter is varried
            if (self.v_max_var):
                ag.v_max = np.random.normal(v_max, v_max*0.1*b, 1)[0]
            if (self.v_desire_var):
                ag.v_desire = np.random.normal(v_desire, v_desire*0.1*b, 1)[0]
            if (self.T_p_var):
                ag.T_p = np.random.normal(T_p, T_p*0.1*b, 1)[0]
            if (self.a_normal_var):
                ag.a_normal = np.random.normal(a_normal, a_normal*0.1*b, 1)[0]                
            if (self.a_max_var):
                ag.a_max = np.random.normal(a_max, a_max*0.1*b, 1)[0]

            return agent_list

    
    def agent_pos_init(self):
        # possible start positions (assures at least one meter of distance between cars)
        start_pos_list = [i for i in range(0, self.track_length, self.car_length+1)]

        agent_list_ordered = []

        for ag in self.agent_list:
            ag.pos_x = start_pos_list.pop(np.random.randint(0, len(start_pos_list)-1)[0])
            
            if (len(agent_list_ordered == 0)):
                agent_list_ordered.append(ag)
            else:
                # binary search
                cur_point = 0
                move_size = max(len(agent_list_ordered)//2, 1)
                while True:
                    # boundary 
                    if (cur_point < 0):
                        cur_point = 0
                    if (cur_point >= len(agent_list_ordered)):
                        cur_point = len(agent_list_ordered)-1
                    
                    cur_pos = agent_list_ordered[cur_point]
                    if (move_size*(cur_pos-ag.pos_x) >= 0):
                        if (move_size*(cur_pos-ag.pos_x) == 0):
                            agent_list_ordered.insert(cur_point, ag)
                            break
                        if (abs(move_size)==1):
                            if (cur_pos> ag.pos_x):
                                agent_list_ordered.insert(cur_point, ag)
                                break
                            else:
                                agent_list_ordered.insert(cur_point+1, ag)
                                break
                        move_size = move_size//2*-1
                    else:
                        if cur_point == 0 and cur_pos>ag.pos_x:
                            agent_list_ordered.insert(cur_point, ag)
                            break
                        if cur_point == len(agent_list_ordered)-1 and cur_pos<ag.pos_x:
                            agent_list_ordered.append(ag)
                            break
                    
                    cur_point += move_size
    
        return agent_list_ordered

                        
    
    # one step of the simulation
    def one_step(self):
        for i in range(self.agent_count):
            ag = self.agent_list_ordered[i]
            ag_front = self.agent_list_ordered[(i+1)% self.agent_count]
            ag.move(ag_front)
    
    # step_count steps of the simulation
    def steps(self, step_count):
        for i in range(step_count):
            self.one_step()
t = Simulation()