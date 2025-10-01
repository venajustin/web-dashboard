from flask import Flask, render_template, send_file
import requests

app = Flask(__name__)

@app.route("/")
def main_page():
        return render_template('index.html')

@app.route("/favicon.ico")
def favicon():
    return send_file('favicon.ico')

@app.route("/workflowy/todo")
def wf_todo():
    r = requests.get("")
    return render_template('workflowy-panel.html')


