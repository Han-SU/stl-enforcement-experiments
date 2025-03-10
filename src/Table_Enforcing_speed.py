
import numpy as np
import Table_transducer as Table_transducer
from Table_transducer import until_transducer
import Table_helper as Table_helper
from Table_helper import Extract_variable_points,Extract_relevant_points,enforcer
from collections import defaultdict
from timeit import default_timer as timer
# import matplotlib.pyplot as plt
import csv
import operator
import os
import pathlib  # Import pathlib

## (speed <= 30)U[5,10] (speed == 0):
###############################################            GENERATING SPEED SIGNAL             ##################################################################################
# Parameters
sampling_rate = 100  # samples per second
total_duration = 11.0  # seconds
time = np.round(np.linspace(0, total_duration, int(total_duration * sampling_rate)), 1)

np.random.seed(0)  # For reproducibility
# Step 1: Define the speed signal with initial value of 30
initial_speed = 30
speed = {t: initial_speed for t in time}

# Step 2: Decay the speed signal to 0 within a random duration of 5-10 seconds
decay_duration = np.random.uniform(5, 10)  # choose a random decay time between 5 and 10 seconds
decay_end_time = decay_duration; 

# # Apply linear decay from 30 to 0 over the decay duration
for t in time:
    if t <= decay_end_time:
        speed[t] = initial_speed * (1 / (1 + np.exp((t - decay_duration / 2) / (0.1 * decay_duration))))#(1 - t / decay_duration)#initial_W * np.exp(-t / decay_duration)
    else:
        speed[t] = 0  # Set speed to 0 after the decay period

###############################################            ENFORCEMENT OF THE SIGNAL             ##################################################################################
#num_noise_points = input("Enter number of noisy points (e.g. 4): ")
num_noise_points=[2,4,6,8,10,12,14,16,18,20] #[4]#[0,10,20,30,40,50,60,70,80,90,100]#[1,2,3,4,5,6,7,8,9,10]
# Create the results directory if it doesn't exist
results_dir = os.getenv('OUTPUT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results'))  # Results dir
os.makedirs(results_dir, exist_ok=True)
file_path = os.path.join(results_dir,"Safe_stopping_of_AVs.csv")  # Create the full path using pathlib
with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["#v", "len", "time(s)"])
        for nnp in num_noise_points:
            ########     ADDING NOISY POINTS  ###############
            print("\n number of noise point=", nnp)
            noise_times = np.random.choice(time[time <= 5], nnp, replace=False)
            speed_copy1 = speed.copy()
            for t in noise_times:
                speed_copy1[t] = np.random.uniform(31, 40)  # Set random noisy speed above 30
            ########     ENCODING SIGNAL  ###############
            # extracting time word
            var_points= Extract_variable_points(speed_copy1, speed_copy1, time, "s<=30.0", "ss==0.0")
            pt1=5.0; pt2=10.0
            var_rel_points,l = Extract_relevant_points(var_points, pt1,pt2)
            #########     ENFORCING PROPERTY ON SIGNAL     ###################
            start = timer()
            enforced_output1=30;enforced_output2=0;
            enforcer(var_rel_points,speed_copy1,speed_copy1, until_transducer,enforced_output1,enforced_output2,pt1,pt2)
            end = timer()
            print(end - start)
            #details = {'#vio': nnp, 'length' :l, 'time taken' : end - start} 
            # with open("/home/saumya/Desktop/STL/STL/speed.csv", "a", newline="") as f:
                # w = csv.writer(f)
                # w.writerow(details.values())
                # writer = csv.writer(f)
                
            
            writer.writerow([nnp, l, end - start])  # Append the values

