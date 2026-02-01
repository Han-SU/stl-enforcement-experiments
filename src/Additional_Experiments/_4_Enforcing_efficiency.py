
# importing packages
import numpy as np
import transducer as transducer
import helper_4 as helper_4
from collections import defaultdict
# from timeit import default_timer as timer
import matplotlib.pyplot as plt
# import csv
import operator
import os

###############################################            CREATING UNTIL TRANSDUCER             ##################################################################################
# Create the until transducer of: (d^2−4v>=0) U[3.01,5] (v^2==0)
Ia=3.01; Ib=5.0   #Ia and Ib are respectively the end points of the interval in the STL formula: (d^2−4v>=0) U[2,5] (v^2==0)

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




###############################################            GENERATING SIGNALS             ##################################################################################
# Generating signals (speed v & distance d) to enforce following STL formula on it: (d^2−4v>=0) U[3.01,5] (v^2==0)
# Parameters
sampling_rate = 100        # samples per second
total_duration = 6.0       # seconds
time = np.linspace(0, total_duration, int(total_duration * sampling_rate))

np.random.seed(4)

# Step 1: Initial values
initial_speed = 20.0
speed = np.zeros_like(time)
distance = np.zeros_like(time)

# Step 2: Speed decay to zero within [3.5, 4.5]
decay_duration = np.random.uniform(3.5, 4.5)

for i, t in enumerate(time):
    if t <= decay_duration:
        speed[i] = initial_speed * (
            1 / (1 + np.exp((t - decay_duration / 2) / (0.15 * decay_duration)))
        )
    else:
        speed[i] = 0.0

# Step 3: Distance coupled to speed (safe region)
distance = 2 * np.sqrt(speed) + 0.5

# --------------------------------------------------
# Step 4: Inject violations
# Strategy:
#   - Increase speed
#   - Decrease distance
#   => d^2 - 4v < 0
# --------------------------------------------------

violation_times = [3.2, 3.6, 4.0, 4.4]   # 4 violations
violation_indices = [np.argmin(np.abs(time - t)) for t in violation_times]

for idx in violation_indices:
    # Increase speed (spike)
    #speed[idx] += 30.0     #increase speed by 30
    delta_v = np.random.uniform(5.0, 10.0)      #increase speed by random amount
    speed[idx] += delta_v

    # Decrease distance sharply
    delta_d = np.random.uniform(4.0, 10.0) 
    distance[idx] -= delta_d

    # Ensure distance stays non-negative (physical constraint)
    distance[idx] = max(distance[idx], 0.1) 

speed_signal = dict(zip(time,speed))
distance_signal = dict(zip(time,distance))



###############################################            EXTRACTING VARIABLE AND RELEVANT POINTS             ##################################################################################
#STL: (d^2−4v>=0) U[3.01,5] (v^2==0)
def find_variable_points1(time, distance, speed):
    #Finds violation points of d^2 - 4v >= 0
    robustness = distance**2 - 4 * speed

    violations = []
    recoveries = []

    i = 0
    n = len(robustness)

    while i < n:
        # Detect start of a violation interval
        if robustness[i] < 0:
            violation_index = i
            violation_time = time[i]
            violations.append((violation_index, violation_time))

            # Search for first recovery after violation
            j = i + 1
            while j < n and robustness[j] < 0:
                j += 1

            if j < n:
                recovery_index = j
                recovery_time = time[j]
                recoveries.append((recovery_index, recovery_time))
                i = j
            else:
                # No recovery found
                break
        else:
            i += 1
    
    times = [t for _, t in violations] + [t for _, t in recoveries]
    timed_word = [[v, "not_a" if i % 2 == 0 else "a"]for i, v in enumerate(sorted(times))]
    timed_word = [[t, label, "not_b"] for t, label in timed_word]

    return timed_word
timed_word1 = find_variable_points1(time, distance, speed)


def find_variable_points2(time, speed, tol=1e-6):
    ##Finds violation points of v^2 == 0
    indices = np.where(np.abs(speed) <= tol)[0]

    if len(indices) == 0:
        return None

    return [[time[indices[0]],"not_a","b"]]
timed_word2 = find_variable_points2(time, speed)
#print(timed_word2)

all_variable_points=sorted(timed_word1+timed_word2)
#print(all_variable_points)


def find_relevent_point():
    #for Ia=3.01
    speed_signal_rounded={round(k, 2): v for k, v in speed_signal.items()}
    v = speed_signal_rounded[Ia]
    distance_signal_rounded={round(k, 2): v for k, v in distance_signal.items()}
    d = distance_signal_rounded[Ia]
    verdict_for_a_at_Ia= (d**2 - 4 * v) >= 0
    verdict_for_b_at_Ia= (v*v==0)
    if verdict_for_a_at_Ia==True:
        string1='a'
    else:
        string1='not_a'
    if verdict_for_b_at_Ia==True:
        string2='b'
    else:
        string2='not_b'     
    relevent_point_1=[Ia,string1,string2]

    #for Ib=5
    speed_signal_rounded={round(k, 2): v for k, v in speed_signal.items()}
    v = speed_signal_rounded[Ib]
    distance_signal_rounded={round(k, 2): v for k, v in distance_signal.items()}
    d = distance_signal_rounded[Ib]
    verdict_for_a_at_Ib= (d**2 - 4 * v) >= 0
    verdict_for_b_at_Ib= (v*v==0)
    if verdict_for_a_at_Ib==True:
        string1='a'
    else:
        string1='not_a'
    if verdict_for_b_at_Ib==True:
        string2='b'
    else:
        string2='not_b'     
    relevent_point_2=[Ib,string1,string2]

    return relevent_point_1, relevent_point_2, [0, 'a', 'not_b']

r1,r2,r3=find_relevent_point()
all_variable_points.extend([r1, r2,r3])
all_variable_points.sort(key=lambda x: x[0])
print(all_variable_points)



######################################################      Constraint solving          ############################################################################################
#enforced_output1= 15
#enforced_output2= 15
"""
def project_to_constraint(v, d):
    # Projects (v, d) to the nearest point satisfying d^2 - 4v >= 0 using Euclidean distance.

    # Solve cubic: d'^3 + (8 - 2v)d' - 8d = 0
    coeffs = [1, 0, (8 - 2*v), -8*d]
    roots = np.roots(coeffs)

    # Keep real roots only
    real_roots = roots[np.isreal(roots)].real

    # Pick root giving minimal distance
    best_d = min(
        real_roots,
        key=lambda dp: (dp - d)**2 + ((dp**2 / 4) - v)**2
    )

    best_v = best_d**2 / 4
    return best_v, best_d
"""
def project_to_constraint_weighted(v, d, alpha=1, beta=1):
    """
    Projects (v, d) to satisfy d^2 - 4v >= 0, preferring changes in v over changes in d.
    Penalize changes in distance d (distance changes are expensive) much more than changes in speed v (speed changes are cheap); 
    so the optimizer prefers to change v and keeps d almost fixed. 
    This is done by minimizing a weighted distance instead of a pure Euclidean one.
    alpha : weight for speed change
    beta  : weight for distance change (beta >> alpha)
    """

    # If already feasible, return unchanged
    if d**2 - 4*v >= 0:
        return v, d

    # Solve weighted projection cubic:
    # d'^3 + (4*beta/alpha - 2*v) d' - (4*beta/alpha) d = 0
    k = 4 * beta / alpha
    coeffs = [1, 0, (k - 2*v), -k*d]

    roots = np.roots(coeffs)

    # Keep real roots only
    real_roots = roots[np.isreal(roots)].real

    # Choose root minimizing weighted distance
    best_d = min(
        real_roots,
        key=lambda dp: alpha * ((dp**2 / 4) - v)**2 + beta * (dp - d)**2
    )

    best_v = best_d**2 / 4
    return best_v, best_d

#################################################################################################################################################
###############################################            ENFORCEMENT OF THE SIGNAL             ##################################################################################
speed_signal_corrected = speed_signal.copy()
distance_signal_corrected = distance_signal.copy()

currState=[until_transducer.get_initial_state(), 0]
# global clock
t = 0 
time_stamps = [event[0] for event in all_variable_points]

for T in range(1, int(max(time_stamps)) + 2): 	# if the last violation was at T=4.6, then T=1,2,3,4,5  

    buffer = [item for item in all_variable_points if T-1 <= item[0] < T] #we assume that events are coming one by one, to look like we r receiving the signal in online fashion
    for i, event in enumerate(buffer):
        currState[1] = event[0] 
        currState, output = until_transducer.make_transition(currState, event[1], event[2],Ia,Ib)	#finding o/p of transition
        if output is not None:
            if output ==1:
                #v = min(speed_signal_corrected[event[0]], distance_signal_corrected[event[0]]**2 / 4)
                #print(speed_signal[round(speed_signal_corrected[event[0]],1)]);exit()
                v_new, d_new = project_to_constraint_weighted(speed_signal_corrected[event[0]], distance_signal_corrected[event[0]])
                speed_signal_corrected[event[0]] = v_new; 
                distance_signal_corrected[event[0]] = d_new; 
            else:
                distance_signal_corrected[event[0]] = 15; 
        if currState[0]=='s2':
            """
            fig, axs = plt.subplots(2, 2, sharex='col', figsize=(14, 6))
            # ---------- Original signals ----------
            axs[0, 0].plot(time, speed)
            axs[0, 0].set_ylabel("signal speed", fontsize=16)
            axs[0, 0].set_title("Original signal speed", fontsize=16)

            axs[1, 0].plot(time, distance)
            axs[1, 0].set_xlabel("Time (seconds)", fontsize=16)
            axs[1, 0].set_ylabel("signal distance", fontsize=16)
            axs[1, 0].set_title("Original signal distance", fontsize=16)

            # ---------- Corrected signals ----------
            speed_corrected = list(speed_signal_corrected.values())
            distance_corrected = list(distance_signal_corrected.values())

            axs[0, 1].plot(time, speed_corrected)
            axs[0, 1].set_ylabel("signal speed", fontsize=16)
            axs[0, 1].set_title("Corrected signal speed", fontsize=16)

            axs[1, 1].plot(time, distance_corrected)
            axs[1, 1].set_xlabel("Time (seconds)", fontsize=16)
            axs[1, 1].set_ylabel("signal distance", fontsize=16)
            axs[1, 1].set_title("Corrected signal distance", fontsize=16)

            plt.tight_layout()
            plt.show()  
            """
            fig, axs = plt.subplots(2, 1, sharex=True, figsize=(14, 6))
            # Extract corrected signals
            speed_corrected = list(speed_signal_corrected.values())
            distance_corrected = list(distance_signal_corrected.values())

            # ---------- Speed subplot ----------
            axs[0].plot(time, speed, label="Original signal", linestyle='--', color='orange')
            axs[0].plot(time, speed_corrected, label="Corrected signal", color='blue')
            axs[0].set_ylabel("signal speed", fontsize=16)
            axs[0].set_title("Original signal vs Corrected Signal", fontsize=16)
            axs[0].legend(fontsize=14)
            axs[0].grid()

            # ---------- Distance subplot ----------
            axs[1].plot(time, distance, label="Original signal", linestyle='--', color='orange')
            axs[1].plot(time, distance_corrected, label="Corrected signal", color='blue')
            axs[1].set_xlabel("Time (seconds)", fontsize=16)
            axs[1].set_ylabel("signal distance", fontsize=16)
            axs[1].set_title("Original signal vs Corrected Signal", fontsize=16)
            axs[1].legend(fontsize=14)
            axs[1].grid()

            plt.tight_layout()
            plt.show()
            exit()

