def read_token():
    token = None
    with open("token", "r") as f:
        token = f.readline()
        return token