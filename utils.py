import json
import re

def save_json(data, filename):
    save_file = open(filename, "w")
    json.dump(data, save_file)


def read_json(filename):
    json_file = open(filename, "r")
    data = json.load(json_file)
    return data

# Password strength validation utility
def is_strong_password(pw):
    """Check if the password is strong: at least 8 chars, upper, lower, digit, special char."""
    if len(pw) < 8:
        return False
    if not re.search(r"[A-Z]", pw):
        return False
    if not re.search(r"[a-z]", pw):
        return False
    if not re.search(r"[0-9]", pw):
        return False
    if not re.search(r"[!@#$%^&*()_+\-=[\]{};':\"\\|,.<>/?]", pw):
        return False
    return True
