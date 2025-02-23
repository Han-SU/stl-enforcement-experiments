
import numpy as np
import Table_transducer as Table_transducer
from Table_transducer import until_transducer,until_transducer2
import Table_helper_for_wheel_motor as Table_helper_for_wheel_motor
from Table_helper_for_wheel_motor import Extract_variable_points1,Extract_variable_points2, Extract_relevant_points,enforcer,warmup_enforcer
from collections import defaultdict
from timeit import default_timer as timer
import csv
# import matplotlib.pyplot as plt
import os
import pathlib  

## (x1 ≤ 30)U[5,10] (x1 = 0) \land (x2 ≤ 30)U[5,10] (x2 = 0)
###############################################            GENERATING SIGNAL             ##################################################################################
# # Parameters
# sampling_rate = 100  # samples per second
# total_duration = 11.0  # seconds
# time = np.round(np.linspace(0, total_duration, int(total_duration * sampling_rate)), 1)
# # Generate random voltage (V) and current (I) signals for two cases:        Voltage starts below 4.2 and gradually approaches it
# np.random.seed(0)  # For reproducibility
# # Signal parameters
# time_steps = 100  # total time steps
# time = np.linspace(0, 10, time_steps)  # simulate over 10 seconds
# # Generate random signal for wheel control (x1) and motor control (x2). Initially below 30, and eventually reaching 0 within 5 to 10 seconds.
# np.random.seed(0)  # for reproducible random values
# # Signal for wheel control (x1): Decreasing to 0 between 5 and 10 seconds
# W = np.maximum(0, 30 - 3 * time + np.random.normal(0, 1, time_steps))
# # Signal for motor control (x2): Decreasing to 0 between 5 and 10 seconds
# M = np.maximum(0, 30 - 3 * time + np.random.normal(0, 1, time_steps))
# # Convert arrays to dictionaries with time as the key
# W = {t: w for t, w in zip(time, W)} #{round(t, 2): round(v, 2) for t, v in zip(time, W)}
# M = {t: m for t, m in zip(time, M)} #{round(t, 2): round(v, 2) for t, v in zip(time, M)}
##################################################################################################
sampling_rate = 100  # samples per second
total_duration = 11.0  # seconds
time = np.round(np.linspace(0, total_duration, int(total_duration * sampling_rate)), 1)
initial_W = 30
W = {t: initial_W for t in time}
decay_duration = np.random.uniform(5, 10)  # choose a random decay time between 5 and 10 seconds
decay_end_time = decay_duration; 
for t in time:
    if t <= decay_end_time:
        W[t] = initial_W * (1 / (1 + np.exp((t - decay_duration / 2) / (0.1 * decay_duration))))#(1 - t / decay_duration)
    else:
        W[t] = 0  # Set speed to 0 after the decay period

np.random.seed(0)  # For reproducibility
initial_M = 20
M = {t: initial_M for t in time}
decay_duration = np.random.uniform(7, 10)  # choose a random decay time between 5 and 10 seconds
decay_end_time = decay_duration; 
for t in time:
    if t <= decay_end_time:
        M[t] = initial_W * (1 - (t / decay_duration) ** 2)#initial_M * (1 - t / decay_duration)
    else:
        M[t] = 0  # Set speed to 0 after the decay period










########################################################################################################
# fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
# ax1.plot(list(W.keys()), list(W.values()), label="Generated signal W", color='orange', linestyle='--')
# ax1.set_xlabel("Time (seconds)", fontsize=14)
# ax1.set_ylabel("signal W", fontsize=14)
# ax1.set_title("Generated signal W", fontsize=16)
# ax1.legend(fontsize=16)
# ax1.grid()

# ax2.plot(list(M.keys()), list(M.values()), label="Generated signal M", color='orange', linestyle='--')
# ax2.set_xlabel("Time (seconds)", fontsize=14)
# ax2.set_ylabel("signal M", fontsize=14)
# ax2.set_title("Generated signal M", fontsize=16)
# ax2.legend(fontsize=16)
# ax2.grid()
# plt.tight_layout()
# plt.show() 
# exit()



###############################################            ADDING NOISE TO THE SIGNAL             ##################################################################################
num_noise_points=[2,4,6,8,10,12,14,16,18,20] #[4]#[0,10,20,30,40,50,60,70,80,90,100]#[1,2,3,4,5,6,7,8,9,10]
# Create the results directory if it doesn't exist
results_dir = os.getenv('OUTPUT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results'))  # Results dir
os.makedirs(results_dir, exist_ok=True)
file_path = os.path.join(results_dir,"Safe_deceleration_of_AVs.csv")  # Create the full path using pathlib
#warmup_enforcer()
with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["#v", "len", "time(s)"])
        for nnp in num_noise_points:
            print("\n number of noise point=", nnp)
            noise_times = np.random.choice(time[time <=8], nnp, replace=False)
            W_copy1 = W.copy()
            M_copy1 = M.copy()
            for t in noise_times:
                W_copy1[t] = np.random.uniform(31,32)  # Set random noisy current above 10
                M_copy1[t] = np.random.uniform(34,39)  # Set random noisy current above 10

            ########     ENCODING SIGNAL  ###############
            print(W[0])
            var_point1= Extract_variable_points1(W_copy1, W_copy1, time, "s<=30.0", "ss==0.0") #(x1 ≤ 10)U[5,10] (x1 = 0) \land (x2 ≤ 30)U[5,10] (x2 = 0)
            var_point2= Extract_variable_points2(M_copy1, M_copy1, time, "s<=30.0", "ss==0.0")
            #print("\n \n var_point1=", var_point1); print("\n var_point2=", var_point2)

            merged_list = var_point1 + var_point2
            merged_list = sorted(merged_list)
            flattened_list = [[time_signal[0], elem1, elem2, elem3, elem4] for (time_signal, elem1, elem2, elem3, elem4) in merged_list]
            #print("\n \n Merged (repetitive) events List:", flattened_list)
            # exit()

            modified_list = Table_helper_for_wheel_motor.club_common_time(flattened_list)
            #print("\n \n  Merged (distinct) events List:", modified_list)

            final_list = Table_helper_for_wheel_motor.final_variable_points(modified_list)
            #print("\n final variable_points:", final_list)
            
            pt1=5.0; pt2=10.0; pt3=5.0; pt4=10.0
            var_rel_points, l = Extract_relevant_points(final_list,pt1,pt2,pt3,pt4)
            


            #########     ENFORCING PROPERTY ON SIGNAL     ###################
            start = timer()
            enforced_output1=30.0; enforced_output2=0.0; enforced_output3=30.0; enforced_output4=0.0       #(x1 ≤ 10)U[5,10] (x1 = 0) \land (x2 ≤ 30)U[5,10] (x2 = 0)
            enforcer(var_rel_points,W_copy1, M_copy1,until_transducer,until_transducer2, enforced_output1,enforced_output2,enforced_output3,enforced_output4, pt1, pt2, pt3, pt4)
            end = timer()
            print(end - start)
            writer.writerow([nnp, l, end - start])  # Append the values

