
string1 = "allocate: 1 -> 2 | 3"
string2 = "allocate: 1 -> "
string3 = "allocate: 1"

for string in [string1, string2, string3]:
    print(string.split(" -> "))
    print(string.split(" -> ")[1].split(" | ") if len(string.split(" -> ")) > 1 else None)
    print(string.split(" -> ")[1].split(" | ")[0] if len(string.split(" -> ")) > 1 else None)
