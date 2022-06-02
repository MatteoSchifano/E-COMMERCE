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
    check, last, ad = GestisciUtente().logIn(user, psw)
    if check == True and ad == 1:
        return render_template("adminwebpage.html", username=user, lastAccess=last, dati=GestisciProdotto().estrai())
    elif check == True and ad == 0:
        return render_template("prodotti.html", username=user, lastAccess=last, dati=GestisciProdotto().estrai())
    else:
        return render_template("login_error.html")


@app.route("/login", methods=["get"])
def getLoginPage():
    return render_template("login.html")


@app.route('/nuovoprodotto', methods=["get"])
def nuovoProdotto():
    return render_template('addproduct.html')


@app.route('/getnuovoprodotto', methods=["post"])
def getNuovoProdotto():
    prod = request.form.get("prodotto")
    produttore = request.form.get("produttore")
    prezzo = request.form.get("prezzo")
    tags = request.form.get("tags")
    product = CreaProdotto(prod, produttore, prezzo, tags)
    product.packProd()
    return render_template('adminwebpage.html', dati=GestisciProdotto().estrai())


if __name__ == '__main__':
    app.run()