

# from graphviz import Digraph


# Helper function to evaluate guard conditions
def evaluate_guard(guard, curr_value,interval1,interval2):
    # Substitute 'x' with the current state's value in the guard e.g. 5<=x<10
    if 't1' in guard:
        guard = guard.replace('t1', str(interval1))
    if 't2' in guard:
        guard = guard.replace('t2', str(interval2))
    guard = guard.replace('x', str(curr_value))
    try:
        return eval(guard)
    except Exception as e:
        print(f"Error evaluating guard: {e}")
        return False
    


class State:
    def __init__(self, name, is_initial=False, is_violation=False):
        self.name = name
        #self.invariant = invarviolationiant
        self.is_initial = is_initial
        self.is_violation = is_violation
        self.transitions = []

    def add_transition(self, target_location, input_action1, input_action2, guard, reset, output):
        self.transitions.append((target_location, input_action1, input_action2, guard, reset, output))


class TimedAutomaton:
    def __init__(self):
        self.states = []

    def add_state(self, state):
        self.states.append(state)

    # def get_state(self, name):
    #     for state in self.states:
    #         if state.name == name:
    #             return state
    #     return None
    
    def get_initial_state(self):
        for state in self.states:
            if state.is_initial:
                return state.name
        return None
    
    


    def visualize(self):
        dot = Digraph()

        for state in self.states:
            if state.is_initial:
                dot.node(state.name, shape='doublecircle', label=state.name)
            elif state.is_violation:
                dot.node(state.name, shape='octagon', label=state.name, style='filled', fillcolor='red')
            else:
                dot.node(state.name, shape='circle', label=state.name)

        for state in self.states:
            for target_location, input_action1, input_action2, guard, reset, output in state.transitions:
                label = f"{input_action1, input_action2}\n"
                if guard:
                    label += f"[guard: {guard}]\n"
                if reset:
                    label += f"[reset: {reset}]\n"
                if output is not None:
                    label += f"[output: {output}]"
                
                dot.edge(state.name, target_location.name, label=label.strip())

        dot.render('timed_automaton', format='png', cleanup=True)  # Change format to 'pdf' if needed
        dot.view()  # This will open the generated image




    def make_transition(self, current_location, action1, action2,interval1,interval2):
        # Get the current state's name and value of x (assuming current_location is a tuple like ('s0', x))
        current_state_name = current_location[0]
        curr_value = current_location[1]
        current_state = None
        
        # Find the current state object from its name
        for state in self.states:
            if state.name == current_state_name:
                current_state = state
                break

        if current_state is None:
            #print(f"No valid state found for: {current_state_name}")
            return current_location, None #None is for output

        # print("\n action1=", action1, "action2=", action2)
        # print(f"        Current State: {current_state.name} (x = {curr_value})")

        # Look for all transitions that match the input action
        for target_location, input_action1, input_action2, guard, reset, output in current_state.transitions:
            if input_action1 == action1 and input_action2 == action2:
                # print(f"        Evaluating transition to {target_location.name} with guard: {guard}")

                # Evaluate guard condition
                if guard is None or evaluate_guard(guard, curr_value,interval1,interval2):
                    # print(f"        Guard satisfied for transition to {target_location.name}")
                    
                    # Reset the value of x if a reset is specified
                    if reset:
                        # Assuming the reset is of the form "x := some_value"
                        reset_value = float(reset.split(':=')[1].strip())
                        curr_value = reset_value
                        # print(f"        x reset to: {curr_value}")

                    # Perform transition
                    # print(f"        Transitioning to {target_location.name}")
                    # print(f"        Output of the transition: {output}")

                    # Update current location to the new state
                    current_location = [target_location.name, curr_value]
                    return current_location, output
                

        #print(f"No valid transition found for action: {action1} from state: {current_state.name}")
        return current_location, None
    

###############################################            CREATING UNTIL TRANSDUCER             ##################################################################################
# Create the until transducer
until_transducer = TimedAutomaton()

# Create states
s0 = State("s0", is_initial=True)
s1 = State("s1")
s2 = State("s2")
s3 = State("s3")

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

# # Store the automaton
# import pickle
# with open('/home/saumya/Desktop/STL/STL/timed_automaton.pkl', 'wb') as f:
#     pickle.dump(until_transducer, f)
# #automaton.visualize()



###############################################            CREATING RELEASE TRANSDUCER             ##################################################################################
# Create the release transducer
release_transducer = TimedAutomaton()

# Create states
s0 = State("s0", is_initial=True)
s1 = State("s1")
s2 = State("s2")
s3 = State("s3")

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

# # Store the automaton
# import pickle
# with open('/home/saumya/Desktop/STL/STL/timed_automaton.pkl', 'wb') as f:
#     pickle.dump(release_transducer, f)
# #automaton.visualize()


























# # Create the automaton
# automaton = TimedAutomaton()

# # Create states
# s0 = State("s0", is_initial=True)
# s1 = State("s1")
# s2 = State("s2")
# violation = State("violation", is_violation=True)

# # Add transitions for s0
# s0.add_transition(s1, "a", None, None, None)
# s0.add_transition(s2, "b", None, "x:=0", None)

# # Add transitions for s1
# s1.add_transition(s1, "a", None, None, None)
# s1.add_transition(s2, "b", None, "x:=0", None)

# # Add transitions for s2
# s2.add_transition(s2, "b", "x==c", "x:=0", 55)
# s2.add_transition(s2, "b", "x<c", None, None)
# s2.add_transition(s1, "a", "x<c", None, None)
# s2.add_transition(violation, "a", "x>c", None, None)
# s2.add_transition(violation, "b", "x>c", None, None)

# # Add transitions for violation
# violation.add_transition(violation, "a", None, None, None)
# violation.add_transition(violation, "b", None, None, None)

# # Add states to automaton
# automaton.add_state(s0)
# automaton.add_state(s1)
# automaton.add_state(s2)
# automaton.add_state(violation)



# # Store the automaton
# import pickle
# with open('/home/saumya/Documents/UoA/HanSu/STL_Enf/timed_automaton.pkl', 'wb') as f:
#     pickle.dump(automaton, f)

# automaton.visualize()




until_transducer2 = TimedAutomaton()

# Create states
s0 = State("s0", is_initial=True)
s1 = State("s1")
s2 = State("s2")
s3 = State("s3")

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