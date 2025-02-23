import Table_transducer as Table_transducer
# import matplotlib.pyplot as plt
import re


def Extract_variable_points1(signal1, signal2, time, proposition1, proposition2):  #"s==4.2", "ss<10"
    # add signal at time=0
    change_points = [(time[0], signal1[0])]
    # Get the ordered list of time keys
    time_keys = list(signal1.keys())

    for i in range(1, len(time_keys)):
        # Access signals using time keys
        current_time = time_keys[i]
        previous_time = time_keys[i - 1]
        
        # Check for change in signal
        #if (signal[current_time] <= 30 and signal[previous_time] > 30) or (signal[current_time] > 30 and signal[previous_time] <= 30):
        #    change_points.append((current_time, signal[current_time]))

        # Replace 'x' in the proposition with the signal at current_time and previous_time
        prop_current = proposition1.replace("s", f"signal1[{current_time}]")
        prop_previous = proposition1.replace("s", f"signal1[{previous_time}]")
        
        # Evaluate the conditions
        condition1 = eval(prop_current) and not eval(prop_previous)
        condition2 = not eval(prop_current) and eval(prop_previous)
        if condition1 or condition2:
            change_points.append((current_time, signal1[current_time]))
    # print(change_points)  

    # form input timed word with the obtained change_points
    inputTimedWord = []
    # searching values in proposition  e.g. "4.2" in s==4.2
    number = re.search(r'\b\d+\.\d+\b', proposition1)
    number = float(number.group(0))
    # searching operator in proposition e.g. ""=="" in s==4.2
    import operator
    operator_maps = {
    "==": operator.eq,
    "<=": operator.le,
    ">=": operator.ge,
    "<": operator.lt,
    ">": operator.gt}
    operatorfound = re.search(r'(==|<=|>=|<|>)', proposition1)
    operatorfound = operatorfound.group()
    comparison_function = operator_maps.get(operatorfound)
    


    # Loop through the first column and alternate between 'a' and 'b'
    for i, value in enumerate(change_points):
        # if i % 2 == 0:
        #     inputTimedWord.append([value, 'a',''])
        # else:
        #     inputTimedWord.append([value, 'not_a',''])
        # if value[1]<=number:
        #     inputTimedWord.append([value, 'a',''])
        # else:
        #     inputTimedWord.append([value, 'not_a',''])
        if comparison_function and comparison_function(value[1], number):
            # print(f"The condition '{value[1]} {operatorfound} {number}' is True.")
            inputTimedWord.append([value, 'a','', '', ''])
        else:
            # print(f"The condition '{value[1]} {operatorfound} {number}' is False.")
            inputTimedWord.append([value, 'not_a','','',''])
    # print("\n inputTimedWord1= ",inputTimedWord)

    ###########################################################################################
    # add signal at time=0
    change_points2 =[(time[0], signal2[0])]
    time_keys2 = list(signal2.keys())


    for i in range(1, len(time_keys2)):
        # Access signals using time keys
        current_time1 = time_keys2[i]
        previous_time1 = time_keys2[i - 1]
        
        # Check for change in signal
        # if (signal[current_time1] == 0 and signal[previous_time1] != 0) or (signal[current_time1] != 0 and signal[previous_time1] == 0):
        #     change_points2.append((current_time1, signal[current_time1]))

        # Replace 'x' in the proposition with the signal at current_time and previous_time
        prop_current = proposition2.replace("ss", f"signal2[{current_time1}]")
        prop_previous = proposition2.replace("ss", f"signal2[{previous_time1}]")
        # Evaluate the conditions
        condition1 = eval(prop_current) and not eval(prop_previous)
        condition2 = not eval(prop_current) and eval(prop_previous)
        if condition1 or condition2:
            change_points2.append((current_time1, signal2[current_time1]))
    # print(change_points2)

    # form input timed word
    inputTimedWord2= []
    # searching values in proposition   e.g. "4.2" in s==4.2
    number = re.search(r'\b\d+\.\d+\b', proposition2);
    number = float(number.group(0))
    # searching operator in proposition e.g. "==" in s==4.2
    import operator
    operator_maps = {
    "==": operator.eq,
    "<=": operator.le,
    ">=": operator.ge,
    "<": operator.lt,
    ">": operator.gt}
    operatorfound = re.search(r'(==|<=|>=|<|>)', proposition2)
    operatorfound = operatorfound.group()
    comparison_function = operator_maps.get(operatorfound)
    
    # Loop through the first column and alternate between 'a' and 'b'
    for i, value in enumerate(change_points2):
        if comparison_function and comparison_function(value[1], number):
            # print(f"The condition '{value[1]} {operatorfound} {number}' is True.")
            inputTimedWord2.append([value, '','b','',''])
        else:
            # print(f"The condition '{value[1]} {operatorfound} {number}' is False.")
            inputTimedWord2.append([value, '','not_b','',''])
    # print("\n inputTimedWord2= ",inputTimedWord2)
    
    
    T = merge_list(inputTimedWord, inputTimedWord2)
    T = club_common_time(T)
    T = final_variable_points(T)
    return T





### HELPER FUNCTIONS FOR VARIABLE POINTS ######################################################
def merge_list(inputTimedWord, inputTimedWord2):
    # finding 1 timed word
    merged_list = inputTimedWord + inputTimedWord2
    merged_list = sorted(merged_list)
    #flattened_list = [[time_signal[0], elem1, elem2, elem3, elem4] for (time_signal, elem1, elem2, elem3, elem4) in merged_list]
    # Output the flattened list
    # print("\n Merged (repetitive) events List:", flattened_list)
    return merged_list


def club_common_time(flattened_list):
    # To modify the list according to following rules: 
    #   1. Identify events with the same time. 
    #   2. Merge those events into a single event containing the common time and fill in non-empty actions at their respective places.
    merged_events = {}
    # Iterate through the events
    for event in flattened_list:
        time, action1, action2, action3, action4 = event
        
        # If the time already exists, update the actions
        if time not in merged_events:
            merged_events[time] = [time, '', '', '', '']  # Initialize with common time and empty actions
        
        # Update non-empty actions
        if action1:
            merged_events[time][1] = action1
        if action2:
            merged_events[time][2] = action2
        if action3:
            merged_events[time][3] = action3
        if action4:
            merged_events[time][4] = action4

    # Convert the dictionary back to a list
    modified_list = list(merged_events.values())
    # Output the modified list
    # print("\n  Merged (distinct) events List:", modified_list)
    return modified_list

def final_variable_points(modified_list):
    final_list = []
    # Iterate over each event in the modified list
    for i in range(len(modified_list)):
        event = modified_list[i]
        
        # If all elements are non-empty, leave it unchanged
        if event[1] and event[2] and event[3] and event[4]:  # Check if action1 and action2 are non-empty
            final_list.append(event)
        else:
            # Replace empty elements with values from the previous event
            if i == 0:  # If it's the first event, we can't replace with anything
                final_list.append(event)
            else:
                prev_event = final_list[-1]
                new_event = [
                    event[0],  # Keep the time
                    event[1] if event[1] else prev_event[1],  # Replace action1 if empty
                    event[2] if event[2] else prev_event[2],   # Replace action2 if empty
                    event[3] if event[3] else prev_event[3],   # Replace action3 if empty
                    event[4] if event[4] else prev_event[4]   # Replace action4 if empty
                ]
                final_list.append(new_event)
    # Output the final modified list
    # print("\n final variable_points:", final_list)
    return final_list
########################################################################################################################## 



def Extract_relevant_points(final_list, pt1, pt2, pt3, pt4):
    # adding relevent points
    # Create new events at t=5 and t=10
    new_events = [[pt1, '', '', '', ''], [pt2, '', '', '', ''], [pt3, '', '', '', ''], [pt4, '', '', '', '']]
    final_list.extend(new_events)
    final_list = sorted(final_list)
    # print("\nfinal_list:", final_list)

    # modifying final_list applying below rules : 
    #   1. if all elements of all events are non-empty, then leave
    #   2. if all elements of any events are empty, then append the actions of the previous event
    modified_final_list = []
    # Iterate through each event in the final list
    for i in range(len(final_list)):
        event = final_list[i]
        
        # Check if the current event has all elements non-empty
        if event[1].strip() and event[2].strip() and event[3].strip() and event[4].strip():  # Check if action1 and action2 are non-empty
            modified_final_list.append(event)
        else:
            # If all elements are empty, replace with previous event actions
            if i > 0:  # Ensure there is a previous event
                previous_event = modified_final_list[-1]  # Get the last appended event
                new_event = [event[0], previous_event[1], previous_event[2], previous_event[3], previous_event[4]]  # Keep time, replace actions
                modified_final_list.append(new_event)
            else:
                # If it's the first event, we cannot replace with anything
                modified_final_list.append(event)

    # remove duplicate lists
    unique_events = []
    seen = set()
    for event in modified_final_list:
        # Convert each event list to a tuple to make it hashable for set operations
        event_tuple = tuple(event)
        if event_tuple not in seen:
            seen.add(event_tuple)
            unique_events.append(event)


    # Output the modified final list
    # print("\n Input timed word for the transducer:", unique_events)
    # print("\nlength of Input timed word:", len(unique_events))
    return unique_events, len(unique_events)





def enforcer(var_rel_points,signal1,signal2,automaton1,automaton2,enforced_output1,enforced_output2,enforced_output3, enforced_output4, interval1,interval2,interval3,interval4):  
    signal1_copy1 = signal1.copy()
    signal2_copy2 = signal2.copy()
    currState1=[automaton1.get_initial_state(), 0]
    currState2=[automaton2.get_initial_state(), 0]
    t = 0 # global clock
    time_stamps = [event[0] for event in var_rel_points]

    for T in range(1, int(max(time_stamps)) + 2): 	# T=1,2,3, ...
        buffer = [item for item in var_rel_points if T-1 <= item[0] < T]
        #print("T=", T-1) 
        for i, event in enumerate(buffer):
            # print("     Event:", event, "...........................................................")
            currState1[1] = event[0] # currState[1] = currState[1] + event[0]
            currState2[1] = event[0]
            currState1, output1 = automaton1.make_transition(currState1, event[1], event[2],interval1,interval2)	#finding o/p of transition
            # print("........................")
            currState2, output2 = automaton2.make_transition(currState2, event[3], event[4],interval3,interval4)
            if output1 is not None:
                #print("\noutput=", output); 
                if output1 ==1:
                    # print("enforced_output1=",enforced_output1)
                    signal1_copy1[round(event[0], 1)] = enforced_output1; #signal[event[0]] = output  # Set the signal at that time point to the output value
                else:
                    # print("enforced_output2=",enforced_output2)
                    signal1_copy1[round(event[0], 1)] = enforced_output2; 
            if output2 is not None:
                #print("\noutput=", output); 
                if output2 ==1:
                    # print("enforced_output3=",enforced_output3)
                    signal2_copy2[round(event[0],1)] = enforced_output3; #signal[event[0]] = output  # Set the signal at that time point to the output value
                else:
                    # print("enforced_output4=",enforced_output4)
                    signal2_copy2[round(event[0],1)] = enforced_output4; 
            if currState1[0]=='s2' and currState2[0]=='s2':
                


                # Plot signal1 in the first figure
                # plt.figure(figsize=(7, 6))
                # plt.plot(list(signal1_copy1.keys()), list(signal1_copy1.values()), label="Corrected signal", color='blue')
                # plt.plot(list(signal1.keys()), list(signal1.values()), label="Original signal", color='orange', linestyle='--')
                # plt.xlabel("Time (seconds)", fontsize=14)
                # plt.ylabel("signal W", fontsize=14)
                # plt.title("Generated signal vs. Enforced signal (Signal 1)", fontsize=16)
                # plt.legend(fontsize=16)
                # plt.grid()
                # plt.show()

                # # Plot signal2 in the second figure
                # plt.figure(figsize=(7, 6))
                # plt.plot(list(signal2_copy2.keys()), list(signal2_copy2.values()), label="Corrected signal", color='blue')
                # plt.plot(list(signal2.keys()), list(signal2.values()), label="Original signal", color='orange', linestyle='--')
                # plt.xlabel("Time (seconds)", fontsize=14)
                # plt.ylabel("signal M", fontsize=14)
                # plt.title("Generated signal vs. Enforced signal (Signal 2)", fontsize=16)
                # plt.legend(fontsize=16)
                # plt.grid()
                # plt.show()

                ##########################################################################
                return
                   
        




def Extract_variable_points2(signal1, signal2, time, proposition1, proposition2):  #"s==4.2", "ss<10"
    # add signal at time=0
    change_points = [(time[0], signal1[0])]
    # Get the ordered list of time keys
    time_keys = list(signal1.keys())

    for i in range(1, len(time_keys)):
        # Access signals using time keys
        current_time = time_keys[i]
        previous_time = time_keys[i - 1]
        
        # Check for change in signal
        #if (signal[current_time] <= 30 and signal[previous_time] > 30) or (signal[current_time] > 30 and signal[previous_time] <= 30):
        #    change_points.append((current_time, signal[current_time]))

        # Replace 'x' in the proposition with the signal at current_time and previous_time
        prop_current = proposition1.replace("s", f"signal1[{current_time}]")
        prop_previous = proposition1.replace("s", f"signal1[{previous_time}]")
        
        # Evaluate the conditions
        condition1 = eval(prop_current) and not eval(prop_previous)
        condition2 = not eval(prop_current) and eval(prop_previous)
        if condition1 or condition2:
            change_points.append((current_time, signal1[current_time]))
    # print(change_points)  

    # form input timed word with the obtained change_points
    inputTimedWord = []
    # searching values in proposition  e.g. "4.2" in s==4.2
    number = re.search(r'\b\d+\.\d+\b', proposition1)
    number = float(number.group(0))
    # searching operator in proposition e.g. ""=="" in s==4.2
    import operator
    operator_maps = {
    "==": operator.eq,
    "<=": operator.le,
    ">=": operator.ge,
    "<": operator.lt,
    ">": operator.gt}
    operatorfound = re.search(r'(==|<=|>=|<|>)', proposition1)
    operatorfound = operatorfound.group()
    comparison_function = operator_maps.get(operatorfound)
    


    # Loop through the first column and alternate between 'a' and 'b'
    for i, value in enumerate(change_points):
        # if i % 2 == 0:
        #     inputTimedWord.append([value, 'a',''])
        # else:
        #     inputTimedWord.append([value, 'not_a',''])
        # if value[1]<=number:
        #     inputTimedWord.append([value, 'a',''])
        # else:
        #     inputTimedWord.append([value, 'not_a',''])
        if comparison_function and comparison_function(value[1], number):
            # print(f"The condition '{value[1]} {operatorfound} {number}' is True.")
            inputTimedWord.append([value,'','', 'c',''])
        else:
            # print(f"The condition '{value[1]} {operatorfound} {number}' is False.")
            inputTimedWord.append([value,'','', 'not_c',''])
    # print("\n inputTimedWord1= ",inputTimedWord)

    ###########################################################################################
    # add signal at time=0
    change_points2 =[(time[0], signal2[0])]
    time_keys2 = list(signal2.keys())


    for i in range(1, len(time_keys2)):
        # Access signals using time keys
        current_time1 = time_keys2[i]
        previous_time1 = time_keys2[i - 1]
        
        # Check for change in signal
        # if (signal[current_time1] == 0 and signal[previous_time1] != 0) or (signal[current_time1] != 0 and signal[previous_time1] == 0):
        #     change_points2.append((current_time1, signal[current_time1]))

        # Replace 'x' in the proposition with the signal at current_time and previous_time
        prop_current = proposition2.replace("ss", f"signal2[{current_time1}]")
        prop_previous = proposition2.replace("ss", f"signal2[{previous_time1}]")
        # Evaluate the conditions
        condition1 = eval(prop_current) and not eval(prop_previous)
        condition2 = not eval(prop_current) and eval(prop_previous)
        if condition1 or condition2:
            change_points2.append((current_time1, signal2[current_time1]))
    # print(change_points2)

    # form input timed word
    inputTimedWord2= []
    # searching values in proposition   e.g. "4.2" in s==4.2
    number = re.search(r'\b\d+\.\d+\b', proposition2);
    number = float(number.group(0))
    # searching operator in proposition e.g. "==" in s==4.2
    import operator
    operator_maps = {
    "==": operator.eq,
    "<=": operator.le,
    ">=": operator.ge,
    "<": operator.lt,
    ">": operator.gt}
    operatorfound = re.search(r'(==|<=|>=|<|>)', proposition2)
    operatorfound = operatorfound.group()
    comparison_function = operator_maps.get(operatorfound)
    
    # Loop through the first column and alternate between 'a' and 'b'
    for i, value in enumerate(change_points2):
        if comparison_function and comparison_function(value[1], number):
            # print(f"The condition '{value[1]} {operatorfound} {number}' is True.")
            inputTimedWord2.append([value,'','','','d'])
        else:
            # print(f"The condition '{value[1]} {operatorfound} {number}' is False.")
            inputTimedWord2.append([value, '','','','not_d'])
    # print("\n inputTimedWord2= ",inputTimedWord2)
    
    
    T = merge_list(inputTimedWord, inputTimedWord2)
    T = club_common_time(T)
    T = final_variable_points(T)
    return T


