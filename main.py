
from DirectoryTree.DirectoryTree import DirectoryTree
from User.User import User

if __name__ == "__main__":
    tree = DirectoryTree()
    users = User.load_users("Data/users.txt")
    tree.initialize_tree(users)
    tree.save_tree("Data/tree.json")

    tree = DirectoryTree.load_tree("Data/tree.json")
    tree.print_tree()
