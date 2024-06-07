import struct

string = b"200 "
integer = 1024
bytes = struct.pack("!4sI", string, integer)
print(bytes)
string, integer = struct.unpack("!4sI", bytes)
print(string, integer)
print(type(string), type(integer))

print(b'200 ' == b'200 ')
