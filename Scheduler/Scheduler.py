
from Scheduler.SlaveStates import SlaveStates
from DirectoryTree.ChunkHandle import ChunkHandle
import threading
import random

class Scheduler:

    def __init__(self, chunk_size: int, n_backups: int):
        self.lock = threading.Lock()
        self.slave_states = SlaveStates()
        self.chunk_size = chunk_size
        self.n_backups = n_backups
        self.debug = True
    
    def debug_print(self, message: str):
        if self.debug:
            print(message)

    def get_message(self, pi_name: str):
        self.lock.acquire()
        message = self.slave_states.get_message(pi_name)
        self.lock.release()
    
    def put_message(self, pi_name: str, message: str):
        self.lock.acquire()
        self.slave_states.put_message(pi_name, message)
        self.lock.release()
    
    def add_pi(self, pi_name: str):
        self.lock.acquire()
        self.slave_states.add_state(pi_name)
        self.lock.release()
    
    def set_capacity(self, pi_name: str, capacity: int):
        self.lock.acquire()
        self.slave_states.set_capacity(pi_name, capacity)
        self.lock.release()
    
    def _reduce_capacity(self, pi_name: str, size: int):
        self.slave_states.reduce_capacity(pi_name, size)
    
    def allocate_chunks(self, size: int, file_path: str):

        n_chunks = size // self.chunk_size + (1 if size % self.chunk_size != 0 else 0)
        allocated = set()
        exclude_pi_names = set()
        chunk_handles = dict()
        self.lock.acquire()
        for i in range(self.n_backups):
            capacities = self.slave_states.get_capacities(exclude_pi_names = allocated)
            n_empty_chunks = [(capicity[0], capicity[1] // self.chunk_size) for capicity in capacities]
            total_empty_chunks = sum([chunk[1] for chunk in n_empty_chunks])
            self.debug_print(f"total_empty_chunks: {total_empty_chunks}, n_chunks: {n_chunks}")
            if total_empty_chunks < n_chunks:
                capacities = self.slave_states.get_capacities(exclude_pi_names = exclude_pi_names)
                n_empty_chunks = [(capicity[0], capicity[1] // self.chunk_size) for capicity in capacities]
                total_empty_chunks = sum([chunk[1] for chunk in n_empty_chunks])
                self.debug_print(f" total_empty_chunks: {total_empty_chunks}, n_chunks: {n_chunks}")
                if total_empty_chunks < n_chunks:
                    self.lock.release()
                    return chunk_handles
            
            chunk_handles[i] = []

            # sort n_empty_chunks by capacity
            n_empty_chunks.sort(key = lambda x: x[1], reverse = True)
            exclude_pi_names.add(n_empty_chunks[0][0])

            # allocate chunks
            cnt_allocated = 0
            pi_list = []
            for pi_name, n_empty_chunk in n_empty_chunks:
                if cnt_allocated + n_empty_chunk >= n_chunks:
                    pi_list.append((pi_name, n_chunks - cnt_allocated))
                    cnt_allocated = n_chunks
                    break
                else:
                    pi_list.append((pi_name, n_empty_chunk))
                    cnt_allocated += n_empty_chunk

            self.debug_print(f"pi_list: {pi_list}")
            
            chunk_cnt = 0
            for pi_name, n_chunk in pi_list:
                for _ in range(n_chunk):
                    chunk_handle = ChunkHandle(
                        location=pi_name,
                        name=f"{file_path}_chunk{chunk_cnt}",
                        fingerprint=str(hex(hash(random.random()))),
                        size=self.chunk_size
                    )
                    chunk_handles[i].append(chunk_handle)
                    chunk_cnt += 1
                    self._reduce_capacity(pi_name, self.chunk_size)
                allocated.add(pi_name)

        self.lock.release()
        return chunk_handles
    
    def _print_state(self):
        self.lock.acquire()
        print(str(self.slave_states))
        self.lock.release()
                    
