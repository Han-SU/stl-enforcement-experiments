
# Packages
import numpy as np
import transducer as transducer
import helper_3 as helper_3
from collections import defaultdict
# from timeit import default_timer as timer
import matplotlib.pyplot as plt
import os

###############################################            CREATING TRANSDUCERS             ##################################################################################
# Create the transducers of: (x1 ≤ 30)U[5,10] (x1 = 0) \land (x2 ≤ 30)U[5,10] (x2 = 0)
# Create the until transducer 1
until_transducer1 = transducer.TimedAutomaton()
# Create states
s0 = transducer.State("s0", is_initial=True)
s1 = transducer.State("s1")
s2 = transducer.State("s2")
s3 = transducer.State("s3")
# Add transitions for s0
s0.add_transition(s1, "a", "b", None, "x:=0", None)
s0.add_transition(s1, "a", "not_b", None, "x:=0", None)
s0.add_transition(s1, "not_a", "b", None, "x:=0", 1)
s0.add_transition(s1, "not_a", "not_b", None, "x:=0", 1)
# Add transitions for s1
s1.add_transition(s1, "a", "b", "x<t1", None, None)
s1.add_transition(s1, "a", "not_b", "x<t1", None, None)
s1.add_transition(s1, "not_a", "b", "x<t1", None, 1)
s1.add_transition(s1, "not_a", "not_b", "x<t1", None, 1)
s1.add_transition(s2, "a", "b", "x==t1", None, None)
s1.add_transition(s2, "not_a", "b", "x==t1", None, 1)
s1.add_transition(s3, "a", "not_b", "x==t1", None, None)
s1.add_transition(s3, "not_a", "not_b", "x==t1", None, 1)
# Add transitions for s3
s3.add_transition(s3, "a", "not_b", "t1<=x<t2", None, None)
s3.add_transition(s3, "not_a", "not_b", "t1<=x<t2", None, 1)
s3.add_transition(s2, "a", "b", "t1<=x<t2", None, None)
s3.add_transition(s2, "not_a", "b", "t1<=x<t2", None, 1)
s3.add_transition(s2, "a", "not_b", "x==t2", None, 2)
s3.add_transition(s2, "not_a", "not_b", "x==t2", None, 2)
# Add states to automaton
until_transducer1.add_state(s0)
until_transducer1.add_state(s1)
until_transducer1.add_state(s2)
until_transducer1.add_state(s3)


# Create the until transducer 2
until_transducer2 = transducer.TimedAutomaton()
# Create states
s0 = transducer.State("s0", is_initial=True)
s1 = transducer.State("s1")
s2 = transducer.State("s2")
s3 = transducer.State("s3")
# Add transitions for s0
s0.add_transition(s1, "c", "d", None, "x:=0", None)
s0.add_transition(s1, "c", "not_d", None, "x:=0", None)
s0.add_transition(s1, "not_c", "d", None, "x:=0", 1)
s0.add_transition(s1, "not_c", "not_d", None, "x:=0", 1)
# Add transitions for s1
s1.add_transition(s1, "c", "d", "x<t1", None, None)
s1.add_transition(s1, "c", "not_d", "x<t1", None, None)
s1.add_transition(s1, "not_c", "d", "x<t1", None, 1)
s1.add_transition(s1, "not_c", "not_d", "x<t1", None, 1)
s1.add_transition(s2, "c", "d", "x==t1", None, None)
s1.add_transition(s2, "not_c", "d", "x==t1", None, 1)
s1.add_transition(s3, "c", "not_d", "x==t1", None, None)
s1.add_transition(s3, "not_c", "not_d", "x==t1", None, 1)
# Add transitions for s3
s3.add_transition(s3, "c", "not_d", "t1<=x<t2", None, None)
s3.add_transition(s3, "not_c", "not_d", "t1<=x<t2", None, 1)
s3.add_transition(s2, "c", "d", "t1<=x<t2", None, None)
s3.add_transition(s2, "not_c", "d", "t1<=x<t2", None, 1)
s3.add_transition(s2, "c", "not_d", "x==t2", None, 2)
s3.add_transition(s2, "not_c", "not_d", "x==t2", None, 2)
# Add states to automaton
until_transducer2.add_state(s0)
until_transducer2.add_state(s1)
until_transducer2.add_state(s2)
until_transducer2.add_state(s3)


###############################################            GENERATING SIGNAL             ##################################################################################
# Parameters
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

# Adding 4 noise/spikes to the signals
noise_times = np.random.choice(time[time <=8], 3, replace=False)        # 3 is the number of current spikes / violations
W_noisy = W.copy()
M_noisy = M.copy()
for t in noise_times:
    W_noisy[t] = np.random.uniform(31,32)  
    M_noisy[t] = np.random.uniform(34,39)  



###############################################            EXTRACTING VARIABLE AND RELEVANT POINTS             ##################################################################################
# var_point1= Extract_variable_points1(W_noisy, W_noisy, time, "s<=30.0", "ss==0.0")       # "s<=30.0" and "ss==0.0" are respectively the LHS and RHS predicates in the STL formula: (x1 ≤ 30)U[5,10] (x1 = 0) 
inputTimedWord1= helper_3.Extract_variable_points(W_noisy, time, "s<=30.0", "a", "not_a", 1)
inputTimedWord2= helper_3.Extract_variable_points(W_noisy, time, "s<=30.0", "b", "not_b", 2)
T = helper_3.merge_list(inputTimedWord1, inputTimedWord2)
T = helper_3.club_common_time(T)
var_point1 = helper_3.final_variable_points(T)
# var_point2= Extract_variable_points2(M_noisy, M_noisy, time, "s<=30.0", "ss==0.0")       # "s<=30.0" and "ss==0.0" are respectively the LHS and RHS predicates in the STL formula: (x2 ≤ 30)U[5,10] (x2 = 0)
inputTimedWord11= helper_3.Extract_variable_points(M_noisy, time, "s<=30.0", "c", "not_c", 3)
inputTimedWord22= helper_3.Extract_variable_points(M_noisy, time, "s<=30.0", "d", "not_d", 4)
T = helper_3.merge_list(inputTimedWord11, inputTimedWord22)
T = helper_3.club_common_time(T)
var_point2 = helper_3.final_variable_points(T)


merged_list = var_point1 + var_point2
merged_list = sorted(merged_list)
flattened_list = [[time_signal[0], elem1, elem2, elem3, elem4] for (time_signal, elem1, elem2, elem3, elem4) in merged_list]
modified_list = helper_3.club_common_time(flattened_list)
final_list = helper_3.final_variable_points(modified_list)

Ia1=5.0; Ib1=10.0   #Ia and Ib are respectively the end points of the interval in the STL formula: (x1 ≤ 30)U[5,10] (x1 = 0)
Ia2=5.0; Ib2=10.0   #Ia and Ib are respectively the end points of the interval in the STL formula: (x2 ≤ 30)U[5,10] (x2 = 0)
var_rel_points, l = helper_3.Extract_relevant_points(final_list,Ia1,Ib1,Ia2,Ib2)

###############################################            ENFORCEMENT OF THE SIGNAL             ##################################################################################
# For the STL formula: (x1 ≤ 30)U[5,10] (x1 = 0) \land (x2 ≤ 30)U[5,10] (x2 = 0), the enforced outputs will be following:
enforced_output1=30.0
enforced_output2=0.0
enforced_output3=30.0
enforced_output4=0.0

W_corrected = W_noisy.copy()
M_corrected = M_noisy.copy()


#enforcer(var_rel_points,W_corrected, M_corrected,until_transducer1,until_transducer2, enforced_output1,enforced_output2,enforced_output3,enforced_output4, Ia1, Ib1, Ia2, Ib2)
currState1=[until_transducer1.get_initial_state(), 0]
currState2=[until_transducer2.get_initial_state(), 0]

# global clock
t = 0 
time_stamps = [event[0] for event in var_rel_points]

for T in range(1, int(max(time_stamps)) + 2): 	# T=1,2,3, ...
    buffer = [item for item in var_rel_points if T-1 <= item[0] < T]
    for i, event in enumerate(buffer):
        currState1[1] = event[0] 
        currState2[1] = event[0]
        currState1, output1 = until_transducer1.make_transition(currState1, event[1], event[2],Ia1, Ib1)	#finding o/p of transition
        currState2, output2 = until_transducer2.make_transition(currState2, event[3], event[4],Ia2, Ib2)
        if output1 is not None:
            if output1 ==1:
                W_corrected[round(event[0], 1)] = enforced_output1
            else:
                W_corrected[round(event[0], 1)] = enforced_output2
        if output2 is not None:
            if output2 ==1:
                M_corrected[round(event[0],1)] = enforced_output3
            else:
                M_corrected[round(event[0],1)] = enforced_output4
        if currState1[0]=='s2' and currState2[0]=='s2': 
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            # Plot signal1 on the first subplot (ax1)
            ax1.plot(list(W_corrected.keys()), list(W_corrected.values()), label="Corrected signal", color='blue')
            ax1.plot(list(W_noisy.keys()), list(W_noisy.values()), label="Original signal", color='orange', linestyle='--')
            ax1.set_xlabel("Time (seconds)", fontsize=14)
            ax1.set_ylabel("signal wheel", fontsize=14)
            ax1.set_title("Original signal vs. Corrected signal", fontsize=16)
            ax1.legend(fontsize=16)
            ax1.grid()

            # Plot signal2 on the second subplot (ax2)
            ax2.plot(list(M_corrected.keys()), list(M_corrected.values()), label="Corrected signal", color='blue')
            ax2.plot(list(M_noisy.keys()), list(M_noisy.values()), label="Original signal", color='orange', linestyle='--')
            ax2.set_xlabel("Time (seconds)", fontsize=14)
            ax2.set_ylabel("signal motor", fontsize=14)
            ax2.set_title("Original signal vs. Corrected signal", fontsize=16)
            ax2.legend(fontsize=16)
            ax2.grid()
            
            # Adjust layout and display the plots
            plt.tight_layout()
            # plt.show() 

            # Save the plot as an image file
            results_dir = os.getenv('OUTPUT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results'))  # Results dir
            os.makedirs(results_dir, exist_ok=True)
            plot_filename = os.path.join(results_dir, "safe_decrease.png")
            plt.savefig(plot_filename, dpi=300)

            print("\n \n open results directory and see the plot:  safe_decrease.png\n ")
            exit()
