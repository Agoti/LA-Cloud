
import queue

class PiState:

    def __init__(self, pi_name: str):
        self.pi_name = pi_name
        self.capacity = None
        self.message_queue_c2s = queue.Queue()
        self.message_queue_s2c = queue.Queue()

class SlaveStates:

    def __init__(self):
        self.states = []

    def add_state(self, pi_name: str):
        if pi_name not in self.get_pi_names():
            self.states.append(PiState(pi_name))
    
    def get_state(self, pi_name: str) -> PiState:
        for state in self.states:
            if state.pi_name == pi_name:
                return state
        return None
    
    def get_message_client(self, pi_name: str):
        state = self.get_state(pi_name)
        if state is not None:
            return state.message_queue_s2c.get()
        return None
    
    def put_message_client(self, pi_name: str, message: str):
        state = self.get_state(pi_name)
        if state is not None:
            state.message_queue_c2s.put(message)
        
    def get_message_slave(self, pi_name: str):
        state = self.get_state(pi_name)
        if state is not None:
            return state.message_queue_c2s.get()
        return None
    
    def put_message_slave(self, pi_name: str, message: str):
        state = self.get_state(pi_name)
        if state is not None:
            state.message_queue_s2c.put(message)

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
    
