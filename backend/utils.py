#helper functions(hashing, file handling)
#handles Reading and writing user data to a JSON file
#password hashing for security

import json
import hashlib
import os   
USERS_FILE=os.path.join("database","users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)
    
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()