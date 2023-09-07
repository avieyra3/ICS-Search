from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
# def index():
#     return "Welcome to my Flask application!"

# @app.route("/about")
# def about():
#     return "This is a simple Flask application created by [Alfonso]."

# @app.route("/user/<Alfonso>")
# def user(name):
#     return f"Hello, {name}! Welcome to my Flask application."

@app.route("/hello")
def hello():
    return render_template("hello.html", name="Flask")

if __name__ == "__main__":
    app.run(debug=True)