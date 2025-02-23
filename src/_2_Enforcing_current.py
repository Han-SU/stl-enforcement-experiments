
# PACKAGES
import numpy as np
import transducer as transducer
import helper_2 as helper_2
from collections import defaultdict
# from timeit import default_timer as timer
import matplotlib.pyplot as plt
# import csv
import os

###############################################            CREATING RELEASE TRANSDUCER             ##################################################################################
# Create the release transducer of: (V==4.2)R[0,10](I<10)
release_transducer = transducer.TimedAutomaton()

# Create states
s0 = transducer.State("s0", is_initial=True)
s1 = transducer.State("s1")
s2 = transducer.State("s2")
s3 = transducer.State("s3")

# Add transitions for s0
s0.add_transition(s1, "not_a", "b", None, "x:=0", None)
s0.add_transition(s1, "not_a", "not_b", None, "x:=0", None)
s0.add_transition(s2, "a", "b", None, "x:=0", None)
s0.add_transition(s2, "a", "not_b", None, "x:=0", None)

# Add transitions for s1
s1.add_transition(s1, "not_a", "b", "x<t1", None, None)
s1.add_transition(s1, "not_a", "not_b", "x<t1", None, None)
s1.add_transition(s2, "a", "b", "x<t1", None, None)
s1.add_transition(s2, "a", "not_b", "x<t1", None, None)
s1.add_transition(s2, "a", "b", "x==t1", None, None)
s1.add_transition(s2, "a", "not_b", "x==t1", None, 2)
s1.add_transition(s3, "not_a", "b", "x==t1", None, None)
s1.add_transition(s3, "not_a", "not_b", "x==t1", None, 2)


# Add transitions for s3
s3.add_transition(s3, "not_a", "b", "t1<=x<t2", None, None)
s3.add_transition(s3, "not_a", "not_b", "t1<=x<t2", None, 2)
s3.add_transition(s2, "a", "b", "t1<=x<t2", None, None)
s3.add_transition(s2, "a", "not_b", "t1<=x<t2", None, 2)
s3.add_transition(s2, "not_a", "not_b", "x==t2", None, 2)
s3.add_transition(s2, "not_a", "b", "x==t2", None, None)


# Add states to automaton
release_transducer.add_state(s0)
release_transducer.add_state(s1)
release_transducer.add_state(s2)
release_transducer.add_state(s3)



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

# include 4 current spikes between 5-10 seconds
noise_times = np.random.choice(time[time <=10], 4, replace=False)   # 4 is the number of current spikes / violations
I_noisy = I.copy()
for t in noise_times:
    I_noisy[t] = np.random.uniform(11,12)  # Set random noisy current above 10
V_noisy = V.copy()

###############################################            EXTRACTING VARIABLE AND RELEVANT POINTS             ##################################################################################
# let the STL formula be (V==4.2)R[0,10](I<10)
var_points= helper_2.Extract_variable_points(V, I_noisy, time, "s==4.2", "ss<10.0")      # "s==4.2" and "ss<10.0" are respectively the LHS and RHS predicates in the STL formula: (V==4.2)R[0,10](I<10)
Ia=5.0; Ib=10.0   #Ia and Ib are respectively the end points of the interval in the STL formula: (V==4.2)R[0,10](I<10)
var_rel_points,l = helper_2.Extract_relevant_points(var_points, Ia, Ib)


###############################################            ENFORCEMENT OF THE SIGNAL             ##################################################################################
# For the STL formula: (V==4.2)R[0,10](I<10), the enforced outputs will be following:
enforced_output1= 4.2
enforced_output2= 9

V_corrected = V_noisy.copy()
I_corrected = I_noisy.copy()

currState=[release_transducer.get_initial_state(), 0]
# global clock
t = 0 
time_stamps = [event[0] for event in var_rel_points]

for T in range(1, int(max(time_stamps)) + 2): 	# T=1,2,3, ...
    buffer = [item for item in var_rel_points if T-1 <= item[0] < T]
    for i, event in enumerate(buffer):
        currState[1] = event[0] 
        currState, output = release_transducer.make_transition(currState, event[1], event[2],Ia,Ib)	#finding o/p of transition
        if output is not None:
            if output ==1:
                V_corrected[round(event[0], 1)] = enforced_output1; 
            else:
                I_corrected[round(event[0], 1)] = enforced_output2; 
        if currState[0]=='s2':
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            # Plot signal1 on the first subplot (ax1)
            ax1.plot(list(V_corrected.keys()), list(V_corrected.values()), label="Corrected signal", color='blue')
            ax1.plot(list(V_noisy.keys()), list(V_noisy.values()), label="Original signal", color='orange', linestyle='--')
            ax1.set_xlabel("Time (seconds)", fontsize=14)
            ax1.set_ylabel("signal voltage", fontsize=14)
            ax1.set_title("Original signal vs. Corrected signal", fontsize=16)
            ax1.legend(fontsize=16)
            ax1.grid()

            # Plot signal2 on the second subplot (ax2)
            ax2.plot(list(I_corrected.keys()), list(I_corrected.values()), label="Corrected signal", color='blue')
            ax2.plot(list(I_noisy.keys()), list(I_noisy.values()), label="Original signal", color='orange', linestyle='--')
            ax2.set_xlabel("Time (seconds)", fontsize=14)
            ax2.set_ylabel("signal current", fontsize=14)
            ax2.set_title("Original signal vs. Corrected signal", fontsize=16)
            ax2.legend(fontsize=16)
            ax2.grid()
            
            # Adjust layout and display the plots
            plt.tight_layout()
            # plt.show() 

            # Save the plot as an image file
            results_dir = os.getenv('OUTPUT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results'))  # Results dir
            os.makedirs(results_dir, exist_ok=True)
            plot_filename = os.path.join(results_dir, "safe_charge.png")
            plt.savefig(plot_filename, dpi=300)

            print("\n \n open results directory and see the plot: safe_charge.png\n ")
            exit()
                                             
  


