from flask import Flask, render_template, send_file, request, make_response
import requests
from dotenv import find_dotenv, load_dotenv
import os
import json
import re

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

@app.route("/canvas/todo")
def canv_todo():
    try:
        selected_courses = json.loads(request.cookies.get("selected_courses"))
    except:
        selected_courses = []

    return render_template('canvas-panel.html', message='Error: not implemented') 


@app.route("/canvas/setcourses", methods=["POST"])
def canv_set_courses():

    dictr = request.form.to_dict()
    
    selected_courses = []
    for course_id, course_enabled in dictr.items():
        if course_enabled == "on":
            selected_courses.append(course_id)

    print("Selected Courses:")
    print(selected_courses)
        
    resp = make_response("""
        <div hx-get="/static/toggle-list-button.html" hx-trigger="load"></div>
    """)

    resp.set_cookie("selected_courses", json.dumps(selected_courses))

    return resp


@app.route("/canvas/coursetoggle")
def canv_courses():

    query = """
    {
          allCourses {
            id
            name
            term {
                name 
            }
          }
    }
    """
    variables = ""

    r = requests.post(url='https://sjsu.instructure.com/api/graphql',
        json={"query": query},
        headers= {
            'Authorization': 'Bearer ' + os.environ.get("CANVAS_API")
        }

    )

    jresp = r.json()

    all_courses = jresp['data']['allCourses']

    try: 
        selected_term = request.values.get('term')
        if selected_term is None: 
            selected_term = json.loads(request.cookies.get("selected_term"))
    except:
        selected_term = "Fall 2025"

    termlist = []
    for course in all_courses:
        if str(course['term']['name']) not in termlist:
             termlist.append(str(course['term']['name']))
             print("appending: ", str(course['term']['name']))



    def course_filter(course):
        return course['term']['name'] == selected_term
           
        
    season_order = {"Spring": 1, "Summer": 2, "Fall": 3, "Winter": 4}
    def semester_key(s):
        if not bool(re.fullmatch(r'(Spring|Summer|Fall|Winter)\s\d{4}', s)):
            return (0, 0)
        season, year = s.split()
        print(season, " : ", year)
        return (int(year), season_order[season])

    filtered_courses = filter(course_filter,all_courses)
    termlist = sorted(termlist, key=semester_key)

    try:
        selected_courses = json.loads(request.cookies.get("selected_courses"))
    except:
        selected_courses = []
    if selected_courses is None:
        selected_courses = []

    resp = make_response(render_template('canvas-course-toggle.html', 
                           courses=filtered_courses, 
                           sel_courses=selected_courses,
                           terms=termlist,
                           selected_term=selected_term))

    resp.set_cookie("selected_term", selected_term)
    return resp

    # if response:
      #      return render_template('workflowy-panel.html', todo_list=todo_list)

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
      
