
# importing packages
import numpy as np
import transducer as transducer
import helper_4 as helper_4
from collections import defaultdict
# from timeit import default_timer as timer
import matplotlib.pyplot as plt
import csv
import time
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





############################################################# VARIABLE and RELEVENT POINTS EXTRACTION
def find_variable_points1(Time, distance, speed):
    robustness = distance**2 - 4 * speed
    violations, recoveries = [], []
    i, n = 0, len(robustness)

    while i < n:
        if robustness[i] < 0:
            violations.append((i, Time[i]))
            j = i + 1
            while j < n and robustness[j] < 0:
                j += 1
            if j < n:
                recoveries.append((j, Time[j]))
                i = j
            else:
                break
        else:
            i += 1

    times = [t for _, t in violations] + [t for _, t in recoveries]
    timed_word = [[v, "not_a" if i % 2 == 0 else "a"] for i, v in enumerate(sorted(times))]
    timed_word = [[t, label, "not_b"] for t, label in timed_word]
    return timed_word


def find_variable_points2(Time, speed, tol=1e-6):
    indices = np.where(np.abs(speed) <= tol)[0]
    if len(indices) == 0:
        return None
    return [[Time[indices[0]], "not_a", "b"]]


def find_relevent_point(speed_signal, distance_signal):
    speed_signal_rounded = {round(k, 2): v for k, v in speed_signal.items()}
    distance_signal_rounded = {round(k, 2): v for k, v in distance_signal.items()}

    def check_point(T):
        v = speed_signal_rounded[T]
        d = distance_signal_rounded[T]
        a = 'a' if (d**2 - 4*v) >= 0 else 'not_a'
        b = 'b' if (v*v == 0) else 'not_b'
        return [T, a, b]

    return check_point(Ia), check_point(Ib), [0, 'a', 'not_b']


############################################################# CONSTRAINT PROJECTION
def project_to_constraint_weighted(v, d, alpha=1, beta=1):
    if d**2 - 4*v >= 0:
        return v, d

    k = 4 * beta / alpha
    coeffs = [1, 0, (k - 2*v), -k*d]
    roots = np.roots(coeffs)
    real_roots = roots[np.isreal(roots)].real

    best_d = min(real_roots,
        key=lambda dp: alpha*((dp**2/4)-v)**2 + beta*(dp-d)**2
    )
    best_v = best_d**2 / 4
    return best_v, best_d




############################################################# GENERATE SIGNALS
# PARAMETERS
sampling_rate = 100
total_duration = 6.0
Time = np.linspace(0, total_duration, int(total_duration * sampling_rate))

Ia = 3.01
Ib = 5.0

np.random.seed(4)

# STEP 1: GENERATE (SAFE) SIGNAL
initial_speed = 20.0
speed_base = np.zeros_like(Time)
distance_base = np.zeros_like(Time)

decay_duration = np.random.uniform(3.5, 4.5)

for i, t in enumerate(Time):
    if t <= decay_duration:
        speed_base[i] = initial_speed * (
            1 / (1 + np.exp((t - decay_duration / 2) / (0.15 * decay_duration)))
        )
    else:
        speed_base[i] = 0.0

distance_base = 2 * np.sqrt(speed_base) + 0.5

# STEP 2: SWEEP NUMBER OF VIOLATIONS
violation_sweep = range(2, 42, 2)   # 2,4,6,...,20
all_runs = {}

for n_violations in violation_sweep:

    # Copy SAME base signal each time
    speed = speed_base.copy()
    distance = distance_base.copy()

    # Spread violations before speed reaches zero
    violation_times = np.linspace(3.0, decay_duration - 0.05, n_violations)
    violation_indices = [np.argmin(np.abs(Time - t)) for t in violation_times]

    for idx in violation_indices:
        speed[idx] += np.random.uniform(5.0, 10.0)
        distance[idx] -= np.random.uniform(4.0, 10.0)
        distance[idx] = max(distance[idx], 0.1)

    speed_signal = dict(zip(Time, speed))
    distance_signal = dict(zip(Time, distance))

    all_runs[n_violations] = (speed_signal, distance_signal)




############################################################## ENFORCEMENT LOOP
results_table = []

for n_violations, (speed_signal, distance_signal) in all_runs.items():
    start_time = time.time()
    print(f"\n================ {n_violations} VIOLATIONS ================")

    speed_arr = np.array(list(speed_signal.values()))
    dist_arr = np.array(list(distance_signal.values()))

    timed_word1 = find_variable_points1(Time, dist_arr, speed_arr)
    timed_word2 = find_variable_points2(Time, speed_arr)
    all_variable_points = sorted(timed_word1 + timed_word2)

    r1, r2, r3 = find_relevent_point(speed_signal, distance_signal)
    all_variable_points.extend([r1, r2, r3])
    all_variable_points.sort(key=lambda x: x[0])

    timed_word_length = len(all_variable_points)

    speed_signal_corrected = speed_signal.copy()
    distance_signal_corrected = distance_signal.copy()

    currState = [until_transducer.get_initial_state(), 0]
    time_stamps = [event[0] for event in all_variable_points]

    for T in range(1, int(max(time_stamps)) + 2):
        buffer = [item for item in all_variable_points if T-1 <= item[0] < T]

        for event in buffer:
            currState[1] = event[0]
            currState, output = until_transducer.make_transition(
                currState, event[1], event[2], Ia, Ib
            )

            if output is not None:
                if output == 1:
                    v_new, d_new = project_to_constraint_weighted(
                        speed_signal_corrected[event[0]],
                        distance_signal_corrected[event[0]]
                    )
                    speed_signal_corrected[event[0]] = v_new
                    distance_signal_corrected[event[0]] = d_new
                else:
                    distance_signal_corrected[event[0]] = 15

            if currState[0] == 's2':
                end_time = time.time()
                elapsed_time = end_time - start_time

                results_table.append([n_violations, timed_word_length, elapsed_time])
                break

with open("/home/saumya/Downloads/STL_2026/src/Exp4/stl_enforcement_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["num_violations", "timed_word_length", "time_taken_sec"])
    writer.writerows(results_table)
    
print("\nResults saved to stl_enforcement_results.csv")

