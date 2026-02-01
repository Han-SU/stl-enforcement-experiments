
# importing packages
import transducer as transducer
import matplotlib.pyplot as plt
import re

def violation_points_of_Proposition_1(time, distance, speed): #Finds time points where the predicate d^2 - 4v >= 0 is violated.
    """
    Parameters:
        time (np.ndarray): time vector
        distance (np.ndarray): distance signal d(t)
        speed (np.ndarray): speed signal v(t)

    Returns:
        violation_indices (np.ndarray): indices where predicate is violated
        violation_times (np.ndarray): corresponding time values
        violation_values (np.ndarray): values of d^2 - 4v at violations
    """
    predicate_values = distance**2 - 4 * speed

    violation_indices = np.where(predicate_values < 0)[0]
    violation_times = time[violation_indices]
    violation_values = predicate_values[violation_indices]

    return violation_indices, violation_times, violation_values
"""
violation_indices, violation_times, violation_values = violation_points_of_Proposition_1(time, distance, speed)
print("Number of violations:", len(violation_indices))
print("Violation times:", violation_times)
print("Predicate values at violations:", violation_values)
"""


def violation_points_of_Proposition_2(time, speed, tol=1e-6):
    """
    Finds the first time instant where v^2 == 0 (i.e., speed == 0).

    Parameters:
        time (np.ndarray): time vector
        speed (np.ndarray): speed signal v(t)
        tol (float): numerical tolerance for zero

    Returns:
        stop_index (int or None): index of first stop
        stop_time (float or None): corresponding time
    """
    stop_indices = np.where(np.abs(speed) <= tol)[0]

    if len(stop_indices) == 0:
        return None, None

    stop_index = stop_indices[0]
    stop_time = time[stop_index]

    return stop_index, stop_time

"""
stop_index, stop_time = violation_points_of_Proposition_2(time, speed)
if stop_index is not None:
    print(f"First stop at t = {stop_time:.3f} s (index {stop_index})")
else:
    print("Speed never reached zero.")
"""
