
class Permission:

    OWNER = "owner"
    GROUP = "group"
    OTHERS = "others"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"

    def __init__(self):
    
        self.permission = {
            "owner": {
                "read": True, 
                "write": True, 
                "execute": True
            },
            "group": {
                "read": False, 
                "write": False,
                "execute": False
            },
            "others": {
                "read": False,
                "write": False,
                "execute": False
            }
        }
    
    def set_permission(self, permission_string):
        # example: rwxr-xr--
        for i, user_type in enumerate([Permission.OWNER, Permission.GROUP, Permission.OTHERS]):
            self.permission[user_type][Permission.READ] = permission_string[i * 3] == "r"
            self.permission[user_type][Permission.WRITE] = permission_string[i * 3 + 1] == "w"
            self.permission[user_type][Permission.EXECUTE] = permission_string[i * 3 + 2] == "x"
    
    def get_permission(self, user_type, permission_type):
        return self.permission[user_type][permission_type]
    
    def __str__(self):
        
        # example: rwxr-xr--
        owner = self.permission["owner"]
        group = self.permission["group"]
        others = self.permission["others"]
        format = ""
        for permission in [owner, group, others]:
            format += "r" if permission["read"] else "-"
            format += "w" if permission["write"] else "-"
            format += "x" if permission["execute"] else "-"
        
        return format
