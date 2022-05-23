import datetime
from pymongo import MongoClient
import hashlib

class MainDb: # gestione db

    def __init__(self, cli = 'mongodb://localhost:37000/', db = 'Iot', coll = 'main'):
        self.cli = cli
        self.db = db
        self.coll = coll

    def connect(self):
        '''
        connessione al db, ricordarsi di chiuderla con client.close()
        ritorna client e coll
        '''
        client = MongoClient(self.cli)
        db = client[self.db]
        coll = db[self.coll]
        return client, coll

    # contiene tutti i metodi generali
    def insertData(self, dct, one=True):
        '''
        inserisce nel database un dizionario chiave valore
        se one = falso inserisce una lista di dizionari
        '''
        client, coll = self.connect()
        if type(dct)==dict and one==True:
            coll.insert_one(dct)
        elif type(dct)==list and one==False:
            coll.insert_many(dct)
        client.close()

    def serchData(self, qwer:dict, proj:dict = None, lim:int = 20):
        '''
        restituisce una lista di dizionari corrispondenti alla qwerry
        '''
        client, coll = self.connect()
        post = coll.find(filter=qwer, projection=proj, limit=lim)
        client.close()
        return post
        

    def updateData(self, fil:dict, new:dict, one=True):
        '''
        aggiorna un documento in base al filtro
        fil: filtro da applicare
        new: nuovo chive/valore da inserire
        one: True update one
        one: False update many
        '''
        client, coll = self.connect()
        if one == True:
            coll.update_one(fil, new)
        else:
            coll.update_many(fil, new)
        client.close()

    def deleteData(self, fil:dict, one=True):
        '''
        elimina un dizionario presente nel db tramite un filtro
        fil: filtro
        one: True delete one
        one: False delete many and return number deleted
        '''
        client, coll = self.connect()
        if one == True:
            coll.delete_one(fil)
        else:
            result = coll.delete_many(fil)
            return result.deleted_count
        client.close()

    def addData(self, idOld, new:dict):
        '''
        aggiorna un documento con un dizionari con stessa chiave e stesso valore
        idOld: _id del dizionario a cui aggiungere delle chiavi/valore
        new: dizionario con le chiavi e con i valori da aggiungere
        '''
        qw = {'_id':idOld}
        val = self.serchData(qw)
        val = dict(val[0])
        val.update(**new)# aggiunge un vaore al json
        self.deleteData(qw)
        self.insertData(val)

class Utente(MainDb):

    def __init__(self,  nome, cognome, username, password, citta, cli='mongodb://localhost:37000/', db='Iot', coll='utente'):
        self.nome = nome
        self.cognome = cognome
        self.username = username
        self.password = self.ahsValue(password)
        self.citta = citta
        self.lastAcc = None       
        super().__init__(cli, db, coll)

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
            self.insertData(dct)
        else:
            return dct

    def ahsValue(self, password:str):
        # crea un ahs costruito con password
        ahs = hashlib.sha256(password.encode('utf-8'))
        # restituisce hash
        return ahs.hexdigest()

    def logIn(self, user, pasw):
        qw = {
                'username':user,
                'password':pasw
             }
        if len(self.serchData(qw)) == 1:
            last = self.serchData(qw)['lastAcc']
            return True, last

class Prodotto(MainDb):

    def __init__(self, nome, produttore, prezzo, cli='mongodb://localhost:37000/', db='Iot', coll='prodotto'):      
        self.nome = nome
        self.produttore = produttore
        self.prezzo = prezzo
        super().__init__(cli, db, coll)
    
    def packProd(self, ins=True):
        '''
        ins: True inserisce nel db
        ins: False ritorna un dizionario con gli attributi dell'oggetto
        '''
        dct = {
                'nome':self.nome,
                'produttore':self.produttore,
                'prezzo':self.prezzo
        }
        if ins == True:
            self.insertData(dct)
        else:
            return dct
