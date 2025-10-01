from flask import Flask, render_template, send_file, request
import requests
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())

app = Flask(__name__)

@app.route("/")
def main_page():
        return render_template('index.html')

@app.route("/favicon.ico")
def favicon():
    return send_file('favicon.ico')

def wf_sort_node(node):
    return node['priority']

@app.route("/workflowy/todo")
def wf_todo():
    r = requests.get("https://workflowy.com/api/v1/nodes",
                     headers={'Authorization': 'Bearer ' + 
                              os.environ.get("WORKFLOWY_API")},
                     params="parent_id=None")
    resp = r.json();
    top_level_nodes = resp["nodes"];
    # print(resp);

    for node in top_level_nodes: 
        if (node["name"] == "TODO"):
            text = "parent_id=" + node['id']
            r2 = requests.get("https://workflowy.com/api/v1/nodes",
                params=text,
                headers={
                    'Authorization': 'Bearer ' + os.environ.get("WORKFLOWY_API"),
                    'Content-type': 'ascii'
                })
                          


            # print(node['id'])
            resp2 = r2.json();
            todo_nodes = resp2["nodes"];
            todo_list = [] 
            for item in todo_nodes:
                todo_list.append(item)
            todo_list.sort(key=wf_sort_node)

            # print(resp2)

            return render_template('workflowy-panel.html', todo_list=todo_list)
    return render_template('workflowy-panel.html', message='Error: no "TODO" node in workflowy')

@app.route("/workflowy/expandnode")
def wf_expand():
    text = "parent_id=" + request.data["node_id"]
    r2 = requests.get("https://workflowy.com/api/v1/nodes",
        params=text,
        headers={
            'Authorization': 'Bearer ' + os.environ.get("WORKFLOWY_API"),
            'Content-type': 'ascii'
        })
                  


    # print(node['id'])
    resp2 = r2.json();
    todo_list = resp2["nodes"];
    # print(resp2)

    return render_template('workflowy-sublist.html', todo_list=todo_list)

@app.route("/testendpoint")
def test():
    # print("testendpoint called <<<<<<<<<<<<<<<<")
    # print(request.data)
    # print("returnign >>>>>>>>>>>>>>>>>>")
    return "success"


"""
curl -G https://workflowy.com/api/v1/nodes \
  -H "Authorization: Bearer [[YOUR_API_KEY]]" \
  -d "parent_id=[[NODE_UUID]]" | jq
"""
      
