from backend.auth import signup, login

print(signup("ashley", "1234"))
print(login("ashley", "1234"))
print(login("ashley", "wrongpass"))
# Test cases for authentication module