
import queue

class PiState:

    def __init__(self, pi_name: str):
        self.pi_name = pi_name
        self.capacity = None
        self.message_queue1 = queue.Queue()
        self.message_queue2 = queue.Queue()

class SlaveStates:

    def __init__(self):
        self.states = []

    def add_state(self, pi_name: str):
        self.states.append(PiState(pi_name))
    
    def get_state(self, pi_name: str) -> PiState:
        for state in self.states:
            if state.pi_name == pi_name:
                return state
        return None
    
    def get_message(self, pi_name: str):
        state = self.get_state(pi_name)
        if state is not None:
            return state.message_queue1.get()
        return None
    
    def put_message(self, pi_name: str, message: str):
        state = self.get_state(pi_name)
        if state is not None:
            state.message_queue2.put(message)

    def set_capacity(self, pi_name: str, capacity: int):
        state = self.get_state(pi_name)
        if state is not None:
            state.capacity = capacity
        else:
            print(f"SlaveStates: set_capacity: {pi_name} not found")
    
    def reduce_capacity(self, pi_name: str, size: int):
        state = self.get_state(pi_name)
        if state is not None:
            state.capacity -= size
        else:
            print(f"SlaveStates: reduce_capacity: {pi_name} not found")
    
    def get_capacity(self, pi_name: str):
        state = self.get_state(pi_name)
        if state is not None:
            return state.capacity
        return None

    def get_pi_names(self):
        return [state.pi_name for state in self.states]

    def remove_state(self, pi_name: str):
        for state in self.states:
            if state.pi_name == pi_name:
                self.states.remove(state)
                return
    
    def __str__(self):
        return "\n".join([f"{state.pi_name}: {state.capacity}" for state in self.states])
    
    def get_capacities(self, exclude_pi_names: set):
        return [(state.pi_name, state.capacity) for state in self.states if state.pi_name not in exclude_pi_names]
    
