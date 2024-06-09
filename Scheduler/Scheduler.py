
from Scheduler.SlaveStates import SlaveStates
from DirectoryTree.ChunkHandle import ChunkHandle
from DirectoryTree.ChunkTable import ChunkTable
from Constants import *
import threading
import random

class Scheduler:

    def __init__(self, 
                 chunk_size: int = CHUNK_SIZE,
                 n_backups: int = N_BACKUPS):
        self.lock = threading.Lock()
        self.slave_states = SlaveStates()
        self.chunk_size = chunk_size
        self.n_backups = n_backups
        self.debug = True
    
    def debug_print(self, message: str):
        if self.debug:
            print(message)

    def get_message_client(self, pi_name: str, timeout = None):
        message = self.slave_states.get_message_client(pi_name, timeout = timeout)
        return message
    
    def put_message_client(self, pi_name: str, message: str):
        self.slave_states.put_message_client(pi_name, message)
    
    def get_message_slave(self, pi_name: str):
        message = self.slave_states.get_message_slave(pi_name)
        return message

    def put_message_slave(self, pi_name: str, message: str):
        self.slave_states.put_message_slave(pi_name, message)
    
    def add_pi(self, pi_name: str):
        self.lock.acquire()
        self.slave_states.add_state(pi_name)
        self.lock.release()
    
    def remove_pi(self, pi_name: str):
        self.lock.acquire()
        self.slave_states.remove_state(pi_name)
        self.lock.release()
    
    def set_capacity(self, pi_name: str, capacity: int):
        self.lock.acquire()
        self.slave_states.set_capacity(pi_name, capacity)
        self.lock.release()
    
    def _reduce_capacity(self, pi_name: str, size: int):
        self.slave_states.reduce_capacity(pi_name, size)
    
    def allocate_chunks(self, size: int, file_path: str) -> dict:

        if size <= 0:
            return None
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
            file_path = file_path.replace("/", "_")
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
        print(str(self.slave_states))
    
    def allocate_request(self, chunk_handles: ChunkTable, master: ChunkTable = None):
        self.lock.acquire()
        # message_builder = "ALLOCATE:\n"
        message_builder = dict()

        # master
        for backup, chunks in master.get_items():
            for j, chunk in enumerate(chunks):
                pi_name = chunk.location
                # message_builder += f"{chunk}\n"
                if pi_name not in message_builder:
                    message_builder[pi_name] = "ALLOCATE:\n"
                message_builder[pi_name] += f"{chunk} -> "
                for i in range(self.n_backups):
                    if i in chunk_handles and i != backup:
                        message_builder[pi_name] += f"{chunk_handles[i][j]} | "
                message_builder[pi_name] = message_builder[pi_name][:-3] + "\n"

        # others
        for i in range(self.n_backups):
            if i in chunk_handles and i not in master:
                for j in range(len(chunk_handles[i])):
                    pi_name = chunk_handles[i][j].location
                    # message_builder += f"{chunk_handles[i][j]}\n"
                    if pi_name not in message_builder:
                        message_builder[pi_name] = "ALLOCATE:\n"
                    message_builder[pi_name] += f"{chunk_handles[i][j]}\n"

        # self.put_message_client(pi_name, message_builder)
        for pi_name, message in message_builder.items():
            self.put_message_client(pi_name, message)
        
            try:
                response = self.get_message_client(pi_name, timeout = ALLOCATE_TIMEOUT)
                if response != "ACK":
                    raise Exception("Response is not ACK: " + response)
            except Exception as e:
                print(f"ACK not received: {e}")
                self.lock.release()
                return False

        self.lock.release()
        return True
    
    def deallocate_request(self, chunk_handles: dict):
        self.lock.acquire()
        message_builder = dict()
        for i in range(self.n_backups):
            if i in chunk_handles:
                for j in range(len(chunk_handles[i])):
                    pi_name = chunk_handles[i][j].location
                    if pi_name not in message_builder:
                        message_builder[pi_name] = "DEALLOCATE:\n"
                    message_builder[pi_name] += f"{chunk_handles[i][j]}\n"
        
        for pi_name, message in message_builder.items():
            self.put_message_client(pi_name, message)
        
            try:
                response = self.get_message_client(pi_name, timeout = ALLOCATE_TIMEOUT)
                if response != "ACK":
                    raise Exception("Response is not ACK" + response)
            except Exception as e:
                print(f"ACK not received: {e}")
                self.lock.release()
                return False

        self.lock.release()
        return True
                    
    def select_backup(self, chunk_table: ChunkTable):

        online_pi_names = self.slave_states.get_pi_names()
        print(f"online_pi_names: {online_pi_names}")
        for backup, chunks in chunk_table.get_items():
            if any([chunk.location not in online_pi_names for chunk in chunks]):
                continue
            return ChunkTable.from_dict({backup: chunks})
        
        return None
