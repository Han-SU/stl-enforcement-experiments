
# importing packages
import numpy as np
import transducer as transducer
import helper_1 as helper_1
from collections import defaultdict
# from timeit import default_timer as timer
import matplotlib.pyplot as plt
# import csv
import operator
import os



###############################################            CREATING UNTIL TRANSDUCER             ##################################################################################
# Create the until transducer of: (speed <= 30)U[5,10] (speed == 0)
until_transducer = transducer.TimedAutomaton()

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
until_transducer.add_state(s0)
until_transducer.add_state(s1)
until_transducer.add_state(s2)
until_transducer.add_state(s3)





###############################################            GENERATING SPEED SIGNAL             ##################################################################################
# Parameters
sampling_rate = 100  # samples per second
total_duration = 11.0  # seconds
time = np.round(np.linspace(0, total_duration, int(total_duration * sampling_rate)), 1)

# Step 1: Define the speed signal with initial value of 30
initial_speed = 30
speed = {t: initial_speed for t in time}
np.random.seed(4)
# Step 2: Decay the speed signal to 0 within a random duration of 5-10 seconds
decay_duration = np.random.uniform(5, 10)  # choose a random decay time between 5 and 10 seconds
decay_end_time = decay_duration; 

# Step 3: Apply linear decay from 30 to 0 over the decay duration
for t in time:
    if t <= decay_end_time:
        speed[t] = initial_speed * (1 / (1 + np.exp((t - decay_duration / 2) / (0.1 * decay_duration))))
    else:
        speed[t] = 0  # Set speed to 0 after the decay period

# Step 4: include 4 speed spikes between 5-10 seconds
noise_times = np.random.choice(time[time <= 5], 4, replace=False) # 4 is the number of speed spikes / violations
speed_noisy = speed.copy()
for t in noise_times:
    speed_noisy[t] = np.random.uniform(31, 40)  # Set random noisy speed above 30




###############################################            EXTRACTING VARIABLE AND RELEVANT POINTS             ##################################################################################
# let the STL formula be (speed <= 30)U[5,10] (speed == 0)
var_points= helper_1.Extract_variable_points(speed_noisy, speed_noisy, time, "s<=30.0", "ss==0.0")   # "s<=30.0" and "ss==0.0" are respectively the LHS and RHS predicates in the STL formula: (speed <= 30)U[5,10] (speed == 0)
Ia=5.0; Ib=10.0   #Ia and Ib are respectively the end points of the interval in the STL formula: (speed <= 30)U[5,10] (speed == 0)
var_rel_points,l = helper_1.Extract_relevant_points(var_points, Ia,Ib)
T_word = var_rel_points
# print("\n Input timed word for the transducer:", T_word)
# print("\n length of Input timed word:", len(T_word))


###############################################            ENFORCEMENT OF THE SIGNAL             ##################################################################################
# For the STL formula: (speed <= 30)U[5,10] (speed == 0), the enforced outputs will be following:
enforced_output1= 30
enforced_output2= 0

speed_corrected = speed_noisy.copy()

currState=[until_transducer.get_initial_state(), 0]
# global clock
t = 0 
time_stamps = [event[0] for event in T_word]

for T in range(1, int(max(time_stamps)) + 2): 	# T=1,2,3, ...
    buffer = [item for item in T_word if T-1 <= item[0] < T]
    for i, event in enumerate(buffer):
        currState[1] = event[0] 
        currState, output = until_transducer.make_transition(currState, event[1], event[2],Ia,Ib)	#finding o/p of transition
        if output is not None:
            if output ==1:
                event_time = round(event[0], 1)
                speed_corrected[event_time] = enforced_output1; 
                # # Update `var_rel_points` item
                # for var_item in var_rel_points:
                #     if round(var_item[0], 1) == event_time:  # Match time with event_time
                #         var_item[1] = enforced_output1  # Update the corresponding item
                #         break  # Stop once we find and update the correct item

            else:
                event_time = round(event[0], 1)
                speed_corrected[event_time] = enforced_output2; 
                # # Update `var_rel_points` item
                # for var_item in var_rel_points:
                #     if round(var_item[0], 1) == event_time:  # Match time with event_time
                #         var_item[1] = enforced_output2  # Update the corresponding item
                #         break  # Stop once we find and update the correct item


        if currState[0]=='s2':
            # printing output timed word
            # print("\n Output timed word from the transducer:", var_rel_points)
            # print("\n length of Input timed word:", len(var_rel_points))

            plt.figure(figsize=(10, 6))
            plt.plot(list(speed_corrected.keys()), list(speed_corrected.values()), label="Corrected signal", color='blue')
            plt.plot(list(speed_noisy.keys()), list(speed_noisy.values()), label="Original signal", color='orange', linestyle='--')
            plt.xlabel("Time (seconds)", fontsize=14)
            plt.ylabel("signal speed", fontsize=14)
            plt.title("Original signal vs. Corrected signal", fontsize=16)
            plt.legend(fontsize=16)
            plt.grid()
            plt.tight_layout()
            #plt.show()


            # Save the plot as an image file
            
            # output_dir = os.environ.get("OUTPUT_DIR", "/app/data") # Allows you to set the output directory through environment variables when running docker
            # if not os.path.exists(output_dir):
            #     os.makedirs(output_dir)
            # filename = "plot_1.png"  # Or whatever you want to name it
            # filepath = os.path.join(output_dir, filename)
            # plt.savefig(filepath)
            # print(f"Plot saved to: {filepath}") #add this to ensure it is working
	    
            results_dir = os.getenv('OUTPUT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results'))  # Results dir
            os.makedirs(results_dir, exist_ok=True)
            plot_filename = os.path.join(results_dir, "safe_stop.png")
            plt.savefig(plot_filename, dpi=300)

            print("\n \n open results directory and see the plot:  safe_stop.png\n ")
            exit()
            
            
            
            
            
            
