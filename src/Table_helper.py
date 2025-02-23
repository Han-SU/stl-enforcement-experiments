import Table_transducer as Table_transducer
# import matplotlib.pyplot as plt
import re


def Extract_variable_points(signal1, signal2, time, proposition1, proposition2):  #"s==4.2", "ss<10"
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
            inputTimedWord.append([value, 'a',''])
        else:
            # print(f"The condition '{value[1]} {operatorfound} {number}' is False.")
            inputTimedWord.append([value, 'not_a',''])
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
            inputTimedWord2.append([value, '','b'])
        else:
            # print(f"The condition '{value[1]} {operatorfound} {number}' is False.")
            inputTimedWord2.append([value, '','not_b'])
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
    print("\n sorted (repetitive) events List:", merged_list)
    flattened_list = [[time_signal[0], elem1, elem2] for (time_signal, elem1, elem2) in merged_list]
    # Output the flattened list
    print("\n Merged (repetitive) events List:", flattened_list)
    return flattened_list


def club_common_time(flattened_list):
    # To modify the list according to following rules: 
    #   1. Identify events with the same time. 
    #   2. Merge those events into a single event containing the common time and fill in non-empty actions at their respective places.
    merged_events = {}
    # Iterate through the events
    for event in flattened_list:
        time, action1, action2 = event
        
        # If the time already exists, update the actions
        if time not in merged_events:
            merged_events[time] = [time, '', '']  # Initialize with common time and empty actions
        
        # Update non-empty actions
        if action1:
            merged_events[time][1] = action1
        if action2:
            merged_events[time][2] = action2

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
        if event[1] and event[2]:  # Check if action1 and action2 are non-empty
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
                    event[2] if event[2] else prev_event[2]   # Replace action2 if empty
                ]
                final_list.append(new_event)
    # Output the final modified list
    # print("\n final variable_points:", final_list)
    return final_list
########################################################################################################################## 



def Extract_relevant_points(final_list, pt1,pt2):
    # adding relevent points
    # Create new events at t=5 and t=10
    new_events = [[pt1, '', ''], [pt2, '', '']]
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
        if event[1].strip() and event[2].strip():  # Check if action1 and action2 are non-empty
            modified_final_list.append(event)
        else:
            # If all elements are empty, replace with previous event actions
            if i > 0:  # Ensure there is a previous event
                previous_event = modified_final_list[-1]  # Get the last appended event
                new_event = [event[0], previous_event[1], previous_event[2]]  # Keep time, replace actions
                modified_final_list.append(new_event)
            else:
                # If it's the first event, we cannot replace with anything
                modified_final_list.append(event)

    # Output the modified final list
    print("\n Input timed word for the transducer:", modified_final_list)
    print("\nlength of Input timed word:", len(modified_final_list))
    return modified_final_list, len(modified_final_list)





def enforcer(var_rel_points,signal1,signal2,automaton,enforced_output1,enforced_output2,interval1,interval2):  
    signal1_copy1 = signal1.copy()
    signal2_copy2 = signal2.copy()
    currState=[automaton.get_initial_state(), 0]
    t = 0 # global clock
    time_stamps = [event[0] for event in var_rel_points]

    for T in range(1, int(max(time_stamps)) + 2): 	# T=1,2,3, ...
        buffer = [item for item in var_rel_points if T-1 <= item[0] < T]
        #print("T=", T-1) 
        for i, event in enumerate(buffer):
            # print("     Event:", event, "...........................................................")
            currState[1] = event[0] # currState[1] = currState[1] + event[0]
            currState, output = automaton.make_transition(currState, event[1], event[2],interval1,interval2)	#finding o/p of transition
            if output is not None:
                #print("\noutput=", output); 
                if output ==1:
                    signal1[round(event[0], 1)] = enforced_output1; #signal[event[0]] = output  # Set the signal at that time point to the output value
                else:
                    signal2[round(event[0], 1)] = enforced_output2; 
            if currState[0]=='s2':
                ################################################################
                # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
                # Plot signal1 on the first subplot (ax1)
                #ax1.plot(list(signal1.keys()), list(signal1.values()), label="enforced signal", color='blue')





                # ax1.plot(list(signal1_copy1.keys()), list(signal1_copy1.values()), label="Generated signal V", color='orange', linestyle='--')
                # ax1.set_xlabel("Time (seconds)", fontsize=14)
                # ax1.set_ylabel("signal V", fontsize=14)
                # ax1.set_title("Generated signal V", fontsize=16)
                # ax1.legend(fontsize=16)
                # ax1.grid()

                # ax2.plot(list(signal2_copy2.keys()), list(signal2_copy2.values()), label="Generated signal I", color='orange', linestyle='--')
                # ax2.set_xlabel("Time (seconds)", fontsize=14)
                # ax2.set_ylabel("signal I", fontsize=14)
                # ax2.set_title("Generated signal I", fontsize=16)
                # ax2.legend(fontsize=16)
                # ax2.grid()
                # # Adjust layout and display the plots
                # plt.tight_layout()
                # plt.show() 

                

                # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
                # # Plot signal1 on the first subplot (ax1)
                # ax1.plot(list(signal1.keys()), list(signal1.values()), label="Corrected signal", color='blue')
                # ax1.plot(list(signal1_copy1.keys()), list(signal1_copy1.values()), label="Original signal", color='orange', linestyle='--')
                # ax1.set_xlabel("Time (seconds)", fontsize=14)
                # ax1.set_ylabel("signal speed", fontsize=14)
                # ax1.set_title("Original signal vs. Corrected signal", fontsize=16)
                # ax1.legend(fontsize=16)
                # ax1.grid()

                # # # Plot signal2 on the second subplot (ax2)
                # # ax2.plot(list(signal2.keys()), list(signal2.values()), label="Corrected signal", color='blue')
                # # ax2.plot(list(signal2_copy2.keys()), list(signal2_copy2.values()), label="Original signal", color='orange', linestyle='--')
                # # ax2.set_xlabel("Time (seconds)", fontsize=14)
                # # ax2.set_ylabel("signal speed", fontsize=14)
                # # ax2.set_title("Original signal vs. Corrected signal", fontsize=16)
                # # ax2.legend(fontsize=16)
                # # ax2.grid()
                # # # Adjust layout and display the plots
                # plt.tight_layout()
                # plt.show() 
                ##########################################################################
                return
                   
        

def warmup_enforcer():
    # ========== 1. 触发模块级初始化 ==========
    # 重新导入模块确保初始化触发（部分环境可能延迟加载）
    import importlib
    import Table_transducer
    importlib.reload(Table_transducer)
    
    dummy_time = [0.0, 1.0]
    dummy_signal = {0.0: 30.0, 1.0: 30.0}

    var_points = Extract_variable_points(
        dummy_signal, dummy_signal, dummy_time, 
        "s<=30.0", "ss==0.0"
    )
    
    var_rel_points, _ = Extract_relevant_points(var_points, 0.5, 1.5)
    
    enforcer(var_rel_points,dummy_signal,dummy_signal,Table_transducer.release_transducer,10.0,14.0,0.5,1.5)
    enforcer(var_rel_points,dummy_signal,dummy_signal,Table_transducer.until_transducer,10.0,14.0,0.5,1.5)    

