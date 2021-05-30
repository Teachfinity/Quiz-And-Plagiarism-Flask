from flask import Flask
from datetime import datetime
import csv, io, re
import urllib, json, random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import request, Flask, render_template, request, jsonify, make_response
from difflib import Differ
import itertools
from ques_generation.generate_questions import get_questions
from flask_cors import CORS

app = Flask(__name__)

""" student_files = [doc for doc in os.listdir() if doc.endswith('.txt')] 

student_notes =[open(File).read() for File in  student_files] """



app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    """ link = "https://firebasestorage.googleapis.com/v0/b/teachfinity-project.appspot.com/o/CSC475_Numerical%20Computing_2nd_Sessional_Final_Version.pdf?alt=media&token=9c356031-e219-42c1-9704-c4161bfdf0b2"
    f = urllib.request.urlopen(link)           
    myfile = f.readline()  
    print(myfile)  """
    return "ok"
    """ plagiarism_results = {"Responses":[]}
    global s_vectors
    for student_a, notes_a, text_vector_a in s_vectors:
        new_vectors =s_vectors.copy()
        current_index = new_vectors.index((student_a, notes_a, text_vector_a))
        del new_vectors[current_index]
        for student_b, notes_b, text_vector_b in new_vectors:
            sim_score = similarity(text_vector_a, text_vector_b)[0][1]
            student_pair = sorted((student_a, student_b))
            score = {"Student1": student_pair[0], "Student2": student_pair[1], "Matches": sim_score*100}
            plagiarism_results["Responses"].append(score)
    return plagiarism_results """

@app.route("/hello/<name>")
def hello_there(name):
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %X")

    # Filter the name argument to letters only using regular expressions. URL arguments
    # can contain arbitrary text, so we restrict to safe characters only.
    match_object = re.match("[a-zA-Z]+", name)

    if match_object:
        clean_name = match_object.group(0)
    else:
        clean_name = "Friend"

    content = "Hello there, " + clean_name + "! It's " + formatted_now
    return content

plagiarism_results = set()

@app.route('/PlagiarismCheck', methods=['GET','POST'])
def PlagiarismCheck():
    # here we want to get the value of the key (i.e. ?key=value)
    if request.method == 'POST':
        json_data = request.get_json()
        names = json_data["studentNames"]
        student_files = json_data["assignments"]
        student_notes = [urllib.request.urlopen(link).readline() for link in  student_files]
        vectorize = lambda Text: TfidfVectorizer().fit_transform(Text).toarray()
        similarity = lambda doc1, doc2: cosine_similarity([doc1, doc2])
        vectors = vectorize(student_notes)
        s_vectors = list(zip(names, vectors))
        s_matches = list(zip(names, student_notes))
        for name_a, text_vector_a in s_vectors:
            new_vectors =s_vectors.copy()
            current_index = new_vectors.index((name_a, text_vector_a)) 
            del new_vectors[current_index]
            for name_b, text_vector_b in new_vectors:
                sim_score = similarity(text_vector_a, text_vector_b)[0][1]
                student_pair = sorted((name_a, name_b))
                score = (student_pair[0], student_pair[1], sim_score*100)
                plagiarism_results.add(score)
        differ = Differ()
        # highlight = {"Data":[], "Responses":[]}
        highlight = []
        responses = []
        for name_a, notes_a in s_matches:
            temp = ""
            string = notes_a.decode("utf-8")
            highlight.append({"name": name_a,"string": string})
            words = string.split('.')
            next = s_matches.copy()
            curr_index = next.index((name_a, notes_a)) 
            del next[curr_index]
            for name_b, notes_b in next:
                temp = ""
                str = notes_b.decode("utf-8")
                word = str.split('.')
                for ws in words:
                    for w in word:
                        alist = differ.compare(ws, w)
                        x = list(alist)
                        for line,nextLine in enumerate(x):
                            # enumerate(list(alist)[:-1])
                            # if (alist[i+1])
                            # print("line: ")
                            # print(nextLine)
                            # print("nextLine: ")
                            # print(alist[])  i+ M + y  name is Mahnoor +i
                            if(x[line-1]!="+" and x[line-1]!="-" and nextLine[0]!="+" and nextLine[0]!="-" ):   
                                #yahan compare next index of line pe plus ya minus to nia
                                # print("current line: ")
                                # print(nextLine)
                                # print("length")
                                # print(len(list(alist)))
                                # if(line<10):
                                    # print("next word: ")
                                    # print(next(nextLine))
                                temp+=nextLine[2]   
                            elif(len(temp)>4):  #My name is
                                # print("Put a break here and empty temp")
                                print(temp)
                                # temp=""
                            else:
                                # print("Not greater than 4 and with + or -")
                                # print(temp)
                                temp=""
                result = (name_a, name_b, temp)
                responses.append(result)
                # highlight["Responses"].append(result)
        print(highlight)
        return {"data": [{"highlight":highlight,"responses":responses}]}
    if request.method == 'GET':
        titles = [('Student 1', 'Student 2', 'Plagiarism Score')]
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(titles)
        cw.writerows(plagiarism_results)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=Results.csv"
        output.headers["Content-type"] = "text/csv"
        return output

@app.route('/converttoText', methods=['GET','POST'])
def converttoText():
    if request.method == 'POST':
        url = request.get_json()
        data = urllib.request.urlopen(url).readline()
        print(data)
        return {"Text": data.decode('utf-8')}

@app.route("/generate_questions", methods=['GET', 'POST'])
def generate_questions():
    text_input = request.get_json()
    question = get_questions(text_input)
    if question == []:
        return {"original": text_input}
    random.shuffle(question)
    return {"original":text_input, "result":question}

def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def build_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response