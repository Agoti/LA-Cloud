
CHUNK_SIZE = 1024 * 1024 * 4
N_BACKUPS = 2
HEARTBEAT_INTERVAL = 5
ALLOCATE_TIMEOUT = 10

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
# DISK = {
#     "pi1": {
#         "path": "VirtualDisk/pi1",
#         "capacity": 100000000
#     },
#     "pi2": {
#         "path": "VirtualDisk/pi2",
#         "capacity": 100000000
#     },
#     "pi3": {
#         "path": "VirtualDisk/pi3",
#         "capacity": 100000000
#     }
# }

MASTER_IP = "10.0.0.1"
SLAVE_IP_PORT = {
    "pi1": {
        "ip": "10.0.0.2",
        "port": 9997,
        "heartbeat": 8887
    },
    "pi2": {
        "ip": "10.0.0.3",
        "port": 9996,
        "heartbeat": 8886
    },
    "pi3": {
        "ip": "10.0.0.4",
        "port": 9995,
        "heartbeat": 8885
    }
}
DISK = {
    "pi1": {
        "path": "file",
        "capacity": 100000000
    },
    "pi2": {
        "path": "file",
        "capacity": 100000000
    },
    "pi3": {
        "path": "file",
        "capacity": 100000000
    }
}

MASTER_CLIENT_PORT = 9999
MASTER_SLAVE_PORT = 9998



