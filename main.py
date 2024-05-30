
from DirectoryTree.DirectoryTree import DirectoryTree
from User.User import User

if __name__ == "__main__":
    tree = DirectoryTree()
    users = User.load_users("Data/users.json")
    print(users[0].privilege)
    # tree.initialize_tree(users)
    # tree.save_tree("Data/tree.json")

    tree = DirectoryTree.load_tree("Data/tree.json")
    tree.print_tree()

    node = tree.get_node("/home/alpt")
    print(node)
    home = tree.get_node("/home")
    print(home)
    print(node == home.get_child("alpt"))
    print(home.list_children())
    root = tree.get_node("/")
    print(root)
    print(root.list_children())

