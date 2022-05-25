from flask import Flask, render_template, request
from back import CreaUtente, GestisciUtente, CreaProdotto, GestisciProdotto, HasH
app = Flask(__name__)


@app.route("/")
def getIndex():
    return render_template("index.html")


@app.route("/doregister", methods=["post"])
def insertUser():
    user = request.form.get("username")
    psw = HasH.ahsValue(request.form.get("password"))
    nome = request.form.get("nome")
    cognome = request.form.get("cognome")
    citta = request.form.get("citta")
    # obj = Utente(nome, cognome, user, citta, psw)
    obj = CreaUtente(nome, cognome, user, psw, citta)
    obj.packUser()
    return render_template("index.html")


@app.route("/register", methods=["get"])
def getSingupPage():
    return render_template("register.html")


@app.route("/dologin", methods=['post'])
def checkCredentials():
    user = request.form.get("username")
    psw = HasH.ahsValue(request.form.get("password"))
    check, last = GestisciUtente().logIn(user, psw)
    if check:
        return render_template("prodotti.html", username=user, lastAccess=last, dati=GestisciProdotto().estrai())
    else:
        return render_template("login_error.html")


@app.route("/login", methods=["get"])
def getLoginPage():
    return render_template("login.html")


@app.route('/nuovoprodotto')
def nuovoProdotto():
    return render_template('setprod.html')

@app.route('/getnuovoprodotto')
def getNuovoProdotto():
    nome = request.form.get('nome')
    produttore = request.form.get('produttore')
    prezzo = request.form.get('prezzo')
    '''password = request.form.get('pasw')
    citta = request.form.get('citta')'''
    obj = CreaProdotto(nome, produttore, prezzo)
    obj.packProd()
    return render_template('table.html')
    
if __name__ == '__main__':
    app.run()