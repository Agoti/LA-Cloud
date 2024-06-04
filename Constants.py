
CHUNK_SIZE = 10
N_BACKUPS = 2

MASTER_IP = "localhost"
SLAVE_IP_PORT = {
    "pi1": {
        "ip": "localhost",
        "port": 9997
    },
    "pi2": {
        "ip": "localhost",
        "port": 9997
    },
    "pi3": {
        "ip": "localhost",
        "port": 9997
    }
}
DISK = {
    "pi1": {
        "path": "VirtualDisk/pi1",
        "capacity": 1000
    },
    "pi2": {
        "path": "VirtualDisk/pi2",
        "capacity": 1000
    },
    "pi3": {
        "path": "VirtualDisk/pi3",
        "capacity": 1000
    }
}

# MASTER_IP = "10.0.0.1"
# SLAVE_IP_PORT = {
#     "pi1": {
#         "ip": "10.0.0.2",
#         "port": 9997
#     },
#     "pi2": {
#         "ip": "10.0.0.3",
#         "port": 9997
#     },
#     "pi3": {
#         "ip": "10.0.0.4",
#         "port": 9997
#     }
# }
# DISK = {
#     "pi1": {
#         "path": "file",
#         "capacity": 1000
#     },
#     "pi2": {
#         "path": "file",
#         "capacity": 1000
#     },
#     "pi3": {
#         "path": "file",
#         "capacity": 1000
#     }
# }

MASTER_CLIENT_PORT = 9999
MASTER_SLAVE_PORT = 9998



