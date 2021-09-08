from flask import Flask
import requests
from requests.api import get
from flask import request
from flask_cors import CORS
import json
import lxml.html as lh
import string
import os


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/returnid")
def returnid():
    file = open("alumnos.json", 'r', encoding="utf8")
    jsonAlu =  json.loads(file.read())
    name = str(request.args.get('name'))
    secName = str(request.args.get('secname'))
    surname = str(request.args.get('surname'))
    if len(secName) > 0:
        contructedName = str(surname + ' ' + name)
        contructedName = contructedName.upper()
        id = jsonAlu.get(contructedName)
    else:
        contructedName = str(surname + ' ' + secName + ' ' + name)
        contructedName = contructedName.upper()
        id = jsonAlu.get(contructedName)
    if id:
        return str(id)
    else:
        return "No id found for " + contructedName 

@app.route("/returnname")
def returnname():
    file = open("ids.json", 'r', encoding="utf8")
    jsonId =  json.loads(file.read())
    id = str(request.args.get('id'))
    name = jsonId.get(id)
    if name:
        return str(name)
    else:
        return "No name found for id " + id
@app.route("/trim1bckp")
def trim1():
    ipmUsername = os.environ.get('ipmUsername', None)
    ipmPassword = os.environ.get('ipmPassword', None)
    r=requests.post('http://www.ipmpadres.com.ar/intranet/aspsql/verifusuario_1.asp?usuario='+ ipmUsername + '&password=' + ipmPassword)
    s = requests.Session()
    aluID = str(request.args.get('id'))
    cookie = r.cookies.get_dict()
    print(r.status_code, cookie, "pad000pre.asp" in r.text)
    if "pad000pre.asp" in str(r.content):
        pad046 = requests.get("http://www.ipmpadres.com.ar/intranet/aspsql/pad046.asp?vTrim=1&vAluSel=" + str(aluID), cookies=cookie)
        parsed_data = lh.fromstring(pad046.content)
        tr_elements = parsed_data.xpath('//tr')
        #Create empty list
        col = {}
        i=0
        #For each row, store each first element (header) and an empty list
        json_data = {}
        for t in range(5, len(tr_elements), 2):
            i+=1
            name=tr_elements[t].text_content().strip()
            content = tr_elements[t+1].text_content().strip().replace("\n", "").replace("\t", "").replace("\r", "").replace("\xa0", " ")
            if ")" in content:
                col[name.strip()] = [content[content.index(")") + 1:len(content)].strip(), content[0:content.index(")") + 1].replace(" )", ")")]
            else:
                col[name.strip()] = [content.strip(), ""]

            json_data = json.dumps(col, ensure_ascii=False).encode('utf8')
        backup = requests.post("https://ipmalumnstrimbackups.herokuapp.com/trim1?id=" + str(aluID) + "&data=" + str(json_data))        
        
        
        print(backup.status_code)
        print(backup.headers)
        return json_data
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)