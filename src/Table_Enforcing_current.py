
import numpy as np
import Table_transducer as Table_transducer
from Table_transducer import release_transducer
import Table_helper as Table_helper
from Table_helper import Extract_variable_points,Extract_relevant_points,enforcer
from collections import defaultdict
from timeit import default_timer as timer
# import matplotlib.pyplot as plt
import csv
import os
import pathlib  


## (V==4.2)R[0,10](I<10)
###############################################            GENERATING SIGNAL             ##################################################################################
# Parameters
sampling_rate = 100  # samples per second
total_duration = 11.0  # seconds
time = np.round(np.linspace(0, total_duration, int(total_duration * sampling_rate)), 1)

# Generate random voltage (V) and current (I) signals for two cases:        Voltage starts below 4.2 and gradually approaches it
np.random.seed(0)  # For reproducibility
V = np.clip(3.8 + 0.05 * np.cumsum(np.random.randn(len(time))), 3.0, 4)
I = np.clip(9 + 0.3 * np.random.randn(len(time)), 5, 12)
# Convert arrays to dictionaries with time as the key
V = {t: v for t, v in zip(time, V)}
I = {t: i for t, i in zip(time, I)}

###############################################            ADDING NOISE TO THE SIGNAL             ##################################################################################
num_noise_points=[2,4,6,8,10,12,14,16,18,20] #[4]#[0,10,20,30,40,50,60,70,80,90,100]#[1,2,3,4,5,6,7,8,9,10]
# Create the results directory if it doesn't exist
results_dir = os.getenv('OUTPUT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results'))  # Results dir
os.makedirs(results_dir, exist_ok=True)
file_path = os.path.join(results_dir,"Safe_charging_of_AVs.csv")  # Create the full path using pathlib
with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["#v", "len", "time(s)"])
        for nnp in num_noise_points:
            print("\n number of noise point=", nnp)
            noise_times = np.random.choice(time[time <=10], nnp, replace=False)
            I_copy1 = I.copy()
            for t in noise_times:
                I_copy1[t] = np.random.uniform(11,12)  # Set random noisy current above 10
            ########     ENCODING SIGNAL  ###############
            # extracting time wordyi
            var_points= Extract_variable_points(V, I_copy1, time, "s==4.2", "ss<10.0")
            pt1=0.0; pt2=10.0   #interval boundaries
            var_rel_points,l = Extract_relevant_points(var_points, pt1,pt2)
            #########     ENFORCING PROPERTY ON SIGNAL     ###################
            start = timer()
            enforced_output1=4.2;enforced_output2=10;
            enforcer(var_rel_points,V, I_copy1,release_transducer,enforced_output1,enforced_output2, pt1, pt2)
            end = timer()
            print(end - start)
            writer.writerow([nnp, l, end - start])  # Append the values


