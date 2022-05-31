def read_token(filename):
    token = None
    with open(filename, "r") as f:
        token = f.readline()
        return token