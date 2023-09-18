from flask import Flask, request, jsonify
from query import Query 
app = Flask(__name__)

@app.route("/")

def index():
    return  open('./templates/index.html').read()

@app.route("/search", methods=['POST'])
def search():
    data: dict = request.get_json()
    userText: str = data['search']
    query = Query()
    result: dict = query.run(userText)
    return result

if __name__ == "__main__":
    app.run(debug=True)