from operator import methodcaller
from flask import Flask, render_template, request
from regex import D
import datetime
app = Flask(__name__)


class Utente:   
    def getLastAccess(self, replace=True):
        resp = self.ultimo_accesso
        if replace: self.ultimo_accesso = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return resp

    def __init__(self, nome: str, cognome: str, username: str, citta: str, password: str):
        self.nome           = nome
        self.cognome        = cognome
        self.username       = username
        self.citta          = citta
        self.password       = password
        self.ultimo_accesso = None


users = [
    Utente('Matteo', 'Schifano', 'teone', 'Pero', '123'),
    Utente('luca', 'koala', 'mogimagi', 'milano', '321'),
    Utente('paolo', 'ronn', 'magisss', 'ancona', 'wondo')
]


@app.route("/")
def getIndex():
    return render_template("index.html")


@app.route("/doregister", methods=["post"])
def insertUser():
    id_ = request.form.get("username")
    psw = request.form.get("password")
    nome = request.form.get("nome")
    cognome = request.form.get("cognome")
    citta = request.form.get("citta")
    users.append(Utente(nome, cognome, id_, citta, psw))
    print(users[-1])
    return render_template("index.html")


@app.route("/register", methods=["get"])
def getSingupPage():
    return render_template("register.html")


@app.route("/dologin", methods=['post'])
def checkCredentials():
    id_ = request.form.get("username")
    psw = request.form.get("password")

    for u in users:
        if u.username == id_ and u.password == psw:
            return render_template("welcome.html", username=id_, lastAccess=u.getLastAccess())
    
    return render_template("login_error.html")


@app.route("/login", methods=["get"])
def getLoginPage():
    return render_template("login.html")


app.run()