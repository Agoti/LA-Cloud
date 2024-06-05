

class Client_Master():
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def login(self):
        username = input("Enter username: ")
        