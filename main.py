
from DirectoryTree.DirectoryTree import DirectoryTree
from DirectoryTree.ChunkHandle import ChunkHandle
from User.User import User
from Scheduler.Scheduler import Scheduler
from Scheduler.SlaveStates import SlaveStates
from ChunkRefs.ChunkRefs import ChunkRefs

if __name__ == "__main__":

    # Test DirectoryTree
    tree = DirectoryTree()
    users = User.load_users("Data/users.json")
    print(users[0].privilege)
    tree.initialize_tree(users)
    tree.save_tree("Data/tree.json")

    # tree = DirectoryTree.load_tree("Data/tree.json")
    # tree.print_tree()
    # node = tree.get_node("/home/alpt")
    # print(node)
    # home = tree.get_node("/home")
    # print(home)
    # print(node == home.get_child("alpt"))
    # print(home.list_children())
    # root = tree.get_node("/")
    # print(root)
    # print(root.list_children())

    # # Test Scheduler
    # scheduler = Scheduler(10, 2)
    # scheduler.add_pi("pi1")
    # scheduler.add_pi("pi2")
    # scheduler.add_pi("pi3")
    # scheduler.set_capacity("pi1", 100)
    # scheduler.set_capacity("pi2", 100)
    # scheduler.set_capacity("pi3", 100)

    # print(scheduler.allocate_chunks(10, "/home/file1.txt"))
    # scheduler._print_states()
    # print(scheduler.allocate_chunks(60, "/home/file2.txt"))
    # scheduler._print_states()
    # print(scheduler.allocate_chunks(70, "/home/file3.txt"))
    # scheduler._print_states()
    # print(scheduler.allocate_chunks(40, "/home/file4.txt"))
    # scheduler._print_states()

    # Test ChunkRefs
    # chunk_refs = ChunkRefs()
    # chunk_1 = ChunkHandle("pi1", "chunk1", "fingerprint", 10)
    # chunk_refs.add_chunk(chunk_1)
    # chunk_refs.save("VirtualDisk/pi1/chunk_refs.json")
