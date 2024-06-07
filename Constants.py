
CHUNK_SIZE = 1024 * 1024 * 4
N_BACKUPS = 2

# MASTER_IP = "localhost"
# SLAVE_IP_PORT = {
#     "pi1": {
#         "ip": "localhost",
#         "port": 9997
#     },
#     "pi2": {
#         "ip": "localhost",
#         "port": 9997
#     },
#     "pi3": {
#         "ip": "localhost",
#         "port": 9997
#     }
# }
DISK = {
    "pi1": {
        "path": "VirtualDisk/pi1",
        "capacity": 100000000
    },
    "pi2": {
        "path": "VirtualDisk/pi2",
        "capacity": 100000000
    },
    "pi3": {
        "path": "VirtualDisk/pi3",
        "capacity": 100000000
    }
}

MASTER_IP = "10.0.0.1"
SLAVE_IP_PORT = {
    "pi1": {
        "ip": "10.0.0.1",
        "port": 9997
    },
    "pi2": {
        "ip": "10.0.0.1",
        "port": 9996
    },
    "pi3": {
        "ip": "10.0.0.1",
        "port": 9995
    }
}
# DISK = {
#     "pi1": {
#         "path": "file",
#         "capacity": 100000000
#     },
#     "pi2": {
#         "path": "file",
#         "capacity": 100000000
#     },
#     "pi3": {
#         "path": "file",
#         "capacity": 100000000
#     }
# }

MASTER_CLIENT_PORT = 9999
MASTER_SLAVE_PORT = 9998



