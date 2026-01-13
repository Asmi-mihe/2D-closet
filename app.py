from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory "database" for demonstration
users = {}

# ------------------ ROUTES ------------------

# Main landing page
@app.route("/")
def index():
    return render_template("index.html")

# Menu page (after auth)
@app.route("/menu")
def menu():
    return render_template("menu.html")

# Closet / Wardrobe page
@app.route("/closet")
def closet():
    return render_template("closet.html")

# Authentication page
@app.route("/auth", methods=["GET", "POST"])
def auth():
    # Determine if login or signup mode
    mode = request.args.get('mode', 'login')
    is_login_mode = (mode == 'login')
    error_msg = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        action = request.form.get("action")  # "login" or "signup"

        if not username or not password:
            error_msg = "Please fill both fields."
        elif action == "login":
            if username in users and users[username] == password:
                # Redirect directly to wardrobe page after login
                return redirect(url_for("closet"))
            else:
                error_msg = "Invalid username or password."
        elif action == "signup":
            if username in users:
                error_msg = "Username already taken!"
            else:
                users[username] = password
                # After signup, go to login page
                return redirect(url_for("auth", mode="login"))

    return render_template(
        "auth.html",
        is_login_mode=is_login_mode,
        error_msg=error_msg
    )

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
