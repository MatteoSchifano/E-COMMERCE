import datetime
from pymongo import MongoClient
from liste import *
import hashlib

class MainDb: # gestione db

    # def __init__(self, cli = 'mongodb://localhost:37000/', db = 'Iot'):
    def __init__(self, cli = 'mongodb://localhost:27017/', db = 'Iot'):
        self.cli = cli
        self.db = db

    def connect(self, coll):
        '''
        connessione al db, ricordarsi di chiuderla con client.close()
        ritorna client e coll
        '''
        client = MongoClient(self.cli)
        db = client[self.db]
        col = db[coll]
        return client, col

    # contiene tutti i metodi generali
    def insertData(self, coll, dct, one=True):
        '''
        inserisce nel database un dizionario chiave valore
        se one = falso inserisce una lista di dizionari
        '''
        client, col = self.connect(coll)
        if type(dct)==dict and one==True:
            col.insert_one(dct)
        elif type(dct)==list and one==False:
            col.insert_many(dct)
        client.close()

    def serchData(self, coll, qwer:dict, proj:dict = None, lim:int = 20):
        '''
        restituisce una lista di dizionari corrispondenti alla qwerry
        '''
        client, col = self.connect(coll)
        post = list(col.find(filter=qwer, projection=proj, limit=lim))
        client.close()
        return post
        

    def updateData(self, coll, fil:dict, new:dict, one=True):
        '''
        aggiorna un documento in base al filtro
        fil: filtro da applicare
        new: nuovo chive/valore da inserire
        one: True update one
        one: False update many
        '''
        client, col = self.connect(coll)
        if one == True:
            col.update_one(fil, new)
        else:
            col.update_many(fil, new)
        client.close()

    def deleteData(self, coll, fil:dict, one=True):
        '''
        elimina un dizionario presente nel db tramite un filtro
        fil: filtro
        one: True delete one
        one: False delete many and return number deleted
        '''
        client, col = self.connect(coll)
        if one == True:
            col.delete_one(fil)
        else:
            result = col.delete_many(fil)
            return result.deleted_count
        client.close()

    def addData(self, coll, idOld, new:dict):
        '''
        aggiorna un documento con un dizionari con stessa chiave e stesso valore
        idOld: _id del dizionario a cui aggiungere delle chiavi/valore
        new: dizionario con le chiavi e con i valori da aggiungere
        '''
        qw = {'_id':idOld}
        val = self.serchData(coll, qw)
        val = dict(val[0])
        val.update(**new)# aggiunge un vaore al json
        self.deleteData(coll, qw)
        self.insertData(val)

class Utente(MainDb):

    coll = 'utente'

    def __init__(self,  nome, cognome, username, password, citta, cli='mongodb://localhost:37000/', db='Iot'):
        self.nome = nome
        self.cognome = cognome
        self.username = username
        self.password = password
        self.citta = citta
        self.lastAcc = None       
        super().__init__(cli, db)
    
    def serchData(self, coll, qwer: dict, proj: dict = None, lim: int = 20):
        return super().serchData(coll, qwer, proj, lim)

    def getLastAccess(self, replace=True):
        resp = self.lastAcc
        if replace: self.lastAcc = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return resp

    def packUser(self, ins=True):
        '''
        ins: True inserisce nel db
        ins: False ritorna un dizionario con gli attributi dell'oggetto
        '''
        
        dct = {
            'nome':self.nome,
            'cognome':self.cognome,
            'username':self.username,
            'password':self.password,
            'citta':self.citta,
            'lastAcc':self.getLastAccess()
        }
        if ins == True:
            self.insertData(self.coll, dct)
        else:
            return dct

def logIn(user, pasw):
    qw = {
            'username':user,
            'password':pasw
            }
    coll = 'utente'
    obj = MainDb()
    qwerry = obj.serchData(coll, qw)
    print(qwerry)
    if len(qwerry)==1:
        last = qwerry[0]['lastAcc']
        return True, last
    else:
        return False, None

def ahsValue(password:str):
    # crea un ahs costruito con password
    ahs = hashlib.sha256(password.encode('utf-8'))
    # restituisce hash
    return ahs.hexdigest()

class Prodotto(MainDb):

    coll='prodotto'

    def __init__(self, nome, produttore, prezzo, tags:list, cli='mongodb://localhost:37000/', db='Iot'):      
        '''crea il prodotto
        tags : lista di tag
        '''        
        self.nome = nome
        self.produttore = produttore
        self.prezzo = prezzo
        self.tags  = tags
        super().__init__(cli, db)
    
    def packProd(self, ins=True):
        '''
        ins: True inserisce nel db
        ins: False ritorna un dizionario con gli attributi dell'oggetto
        '''
        dct = {
                'nome':self.nome,
                'produttore':self.produttore,
                'prezzo':self.prezzo,
                'tags':self.tags
        }
        if ins == True:
            self.insertData(self.coll, dct)
        else:
            return dct

if __name__ == '__main__':
    nome = prodotti
    produttore = produttori
    prezzo = prezzi
    print(tags)
    for x,y,z,t in zip(nome, produttore, prezzo, tags):
        obj = Prodotto(x,y,z,t, cli='mongodb://localhost:27017/')
        obj.packProd()
