#Login and signup logic
# This module handles user authentication, including login and signup functionalities.
#file exposes functions that the frontend might call later

from backend.utils import load_users, save_users, hash_password

def signup(username: str, password: str):
    users = load_users()
    if username in users:
        return False  # User already exists
    users[username] = {
        "password": hash_password(password)
    }
    save_users(users)
    return True, "Signup successful"

def login(username: str, password: str):
    users = load_users()
    if username not in users:
        return False  # User does not exist
    if users[username]["password"] != hash_password(password):
        return False  # Incorrect password
    return True, "Login successful"