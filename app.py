from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/closet")
def closet():
    return render_template("closet.html")  # if you have this page

if __name__ == "__main__":
    app.run(debug=True)
