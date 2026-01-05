# Login and signup logic
# This module handles user authentication, including login and signup functionalities.
# File exposes functions that the frontend might call.

from backend.utils import load_users, save_users, hash_password

# -------------------- SIGNUP --------------------
def signup(username: str, email: str, password: str):
    """
    Creates a new user account.

    Args:
        username (str): Desired username
        email (str): User email
        password (str): Plaintext password

    Returns:
        tuple: (success: bool, message: str)
    """
    if not username or not email or not password:
        return False, "All fields are required"

    users = load_users()

    # Check for duplicate username
    if username in users:
        return False, "Username already exists"

    # Check for duplicate email
    for user in users.values():
        if user.get("email") == email:
            return False, "Email already exists"

    # Save user
    users[username] = {
        "email": email,
        "password": hash_password(password)
    }
    save_users(users)
    return True, "Signup successful"


# -------------------- LOGIN --------------------
def login(username_or_email: str, password: str):
    """
    Logs in a user using username or email.

    Args:
        username_or_email (str): Username or email
        password (str): Plaintext password

    Returns:
        tuple: (success: bool, message: str)
    """
    if not username_or_email or not password:
        return False, "Both fields are required"

    users = load_users()
    hashed_password = hash_password(password)

    # Search for user by username or email
    for username, info in users.items():
        if username_or_email == username or username_or_email == info.get("email"):
            if info.get("password") == hashed_password:
                return True, "Login successful"
            else:
                return False, "Incorrect password"

    return False, "User not found"


# -------------------- TEST --------------------
if __name__ == "__main__":
    # Simple test cases
    print(signup("ashley", "ashley@example.com", "1234"))
    print(login("ashley", "1234"))
    print(login("ashley@example.com", "1234"))
    print(login("ashley", "wrongpass"))
    print(signup("ashley", "ashley@example.com", "1234"))  # duplicate
