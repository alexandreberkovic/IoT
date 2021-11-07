from flask import Flask, Response
import json

app = Flask(__name__)

@app.route('/assignment_callback', methods=['POST','GET'])
def assignment_callback():
    """For now, we will respond to assignment callbacks with empty 200 response"""
    resp = Response({}, status = 200, mimetype = 'application/json')
    return resp

if __name__ == "__main__":
    app.run(debug=True)
