# ALL OPERATIONS RELATED TO TRANSDUCER
#from graphviz import Digraph


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

        # Look for all transitions that match the input action
        for target_location, input_action1, input_action2, guard, reset, output in current_state.transitions:
            if input_action1 == action1 and input_action2 == action2:

                # Evaluate guard condition
                if guard is None or evaluate_guard(guard, curr_value,interval1,interval2):
                    
                    # Reset the value of x if a reset is specified
                    if reset:
                        # Assuming the reset is of the form "x := some_value"
                        reset_value = float(reset.split(':=')[1].strip())
                        curr_value = reset_value

                    # Update current location to the new state
                    current_location = [target_location.name, curr_value]
                    return current_location, output
                
        return current_location, None
    







