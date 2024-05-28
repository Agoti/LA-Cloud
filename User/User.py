
class User:

    USER = "user"
    ROOT = "root"

    def __init__(self, 
                 name,
                 encrypted_password,
                 groups = [],
                 privilage = USER):
        
        self.name = name
        self.encrypted_password = encrypted_password
        self.groups = groups

        assert privilage in [User.USER, User.ROOT], "Invalid privilage"
        self.privilage = privilage
    
    def __repr__(self):
        return self.name
    
    def to_dict(self):
        return {
            "name": self.name,
            "encrypted_password": self.encrypted_password,
            "groups": self.groups,
            "privilage": self.privilage
        }
    
    @staticmethod
    def from_dict(dict):
        if dict is None:
            return None
        return User(dict["name"],
                    dict["encrypted_password"],
                    dict["groups"],
                    dict["privilage"])
    

    @staticmethod
    def exists(users, name):
        for user in users:
            if user.name == name:
                return True
        return False
    
    @staticmethod
    def verify_user(users, name, encrypted_password):
        for user in users:
            if user.name == name:
                if user.encrypted_password == encrypted_password:
                    return None, user
                return "Incorrect password", None
        return "User not found", None
    
    @staticmethod
    def get_root(users):
        for user in users:
            if user.privilage == User.ROOT:
                return user
        return None
    
    @staticmethod
    def save_users(users, path):
        with open(path, "w") as file:
            for user in users:
                file.write(user.name + "\n")
                file.write(user.encrypted_password + "\n")
                file.write(" ".join(user.groups) + "\n")
    
    @staticmethod
    def load_users(path):
        users = []
        with open(path, "r") as file:
            lines = file.readlines()
            for i in range(0, len(lines), 3):
                users.append(User(lines[i].strip(), lines[i + 1].strip(), lines[i + 2].strip().split(" ")))
        
        return users


if __name__ == "__main__":

    from Cipher import MD5Cipher
    try:
        admin = User(name='admin',
                    encrypted_password=MD5Cipher.encrypt('admin'),
                    groups=['admin'],
                    privilage=User.ROOT)
        lmx = User(name='lmx',
                encrypted_password=MD5Cipher.encrypt('lmx'),
                groups=['thu', 'lmx'],
                privilage=User.USER)
        alpt = User(name='alpt',
                    encrypted_password=MD5Cipher.encrypt('alpt'),
                    groups=['thu', 'alpt'],
                    privilage=User.USER)
        users = [admin, lmx, alpt]
    except AssertionError as e:
        print(e)

    User.save_users(users, "Data/users.txt")
    users = User.load_users("Data/users.txt")
    print(users)

