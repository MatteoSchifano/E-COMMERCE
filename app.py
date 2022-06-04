from flask import Flask, render_template, request
from back import CorreletedProduct, CreaUtente, GestisciUtente, CreaProdotto, GestisciProdotto, HasH
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


@app.route('/returntoprodotti')
def tornaIndietro():
    return render_template('prodotti.html', dati=GestisciProdotto().estrai())


@app.route('/prodotti_correlati', methods=["POST"])
def prodottiCorrelati():
    prodotto_acquistato = dict(request.form)['prodotto_acquistato']
    print(prodotto_acquistato[18:42], type(prodotto_acquistato))
    
    # esempio di stampa
    # prodotto_acquistato = """{'_id': ObjectId('6298a0313491ed1f6804477a'), 'nome': 'White ^un^ Coaches Flex Slouch Hat',
    #  'produttore': 'Adidas', 'prezzo': 28, 'tags': 'Clothing & Accessories,Men,Hats'}"""
    # passando questi dati al back tramite query troviamo il prodotto acquistato.
    return render_template('prodotti_correlati.html', dati=CorreletedProduct().prodotti_correlati(prodotto_acquistato[18:42]))


if __name__ == '__main__':
    app.run()
