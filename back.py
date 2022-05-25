import datetime
from pymongo import MongoClient
from liste import *
import hashlib

class MainDb: # gestione db

    def __init__(self, cli = 'mongodb://localhost:37000/', db = 'Iot'):
    # def __init__(self, cli = 'mongodb://localhost:27017/', db = 'Iot'):
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
        new_val = {"$set":new}
        client, col = self.connect(coll)
        if one == True:
            col.update_one(fil, new_val)
        else:
            col.update_many(fil, new_val)
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

class HasH:

    def ahsValue(password:str):
        # crea un ahs costruito con password
        ahs = hashlib.sha256(password.encode('utf-8'))
        # restituisce hash
        return ahs.hexdigest()
    
    def confontaPass(pasw1:str, pasw2:str):
        if pasw1 == pasw2:
            return True
        else:
            return False

class GestisciUtente(MainDb):

    coll = 'utente'

    def updateDataAccess(self, doc:dict, one=True):
        fil = {'_id':doc['_id']}
        new = {'lastAcc': self.lastAccess()}
        return super().updateData(self.coll, fil, new, one)

    def serchDataUtente(self, qwer: dict, proj: dict = None, lim: int = 20):
        return super().serchData(self.coll, qwer, proj, lim)

    def insertDataUtente(self, dct, one=True):   
        return super().insertData(self.coll, dct, one)

    def logIn(self, user, pasw):
        qw =    {
                'username':user,
                'password':pasw
                }

        qwerry = self.serchDataUtente(qw)
        if len(qwerry)==1:
            last = qwerry[0]['lastAcc']
            self.updateDataAccess(qwerry[0])
            return True, last
        else:
            return False, None
            
    def lastAccess(self):
        '''
        ritorna una variabile con data e ora attuale
        '''
        resp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return resp

class CreaUtente(GestisciUtente):

    def __init__(self,  nome, cognome, username, password, citta):
        self.nome = nome
        self.cognome = cognome
        self.username = username
        self.password = password
        self.citta = citta
        self.lastAcc = self.lastAccess()       
        super().__init__()

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
            'lastAcc':self.lastAcc
        }
        if ins == True:
            self.insertDataUtente(dct)
        else:
            return dct

class GestisciProdotto(MainDb):

    coll='prodotto'

    def serchDataProdotto(self, qwer: dict, proj: dict = None, lim: int = 20):
        return super().serchData(self.coll, qwer, proj, lim)
    
    def insertDataProdotto(self, dct, one=True):
        return super().insertData(self.coll, dct, one)

    def estrai(self):
        '''
        estrae tutti i documenti presenti nella collezione prodotto
        '''
        lst = list(self.serchDataProdotto(qwer={}))
        return lst

class CreaProdotto(GestisciProdotto):

    def __init__(self, nome, produttore, prezzo, tags:list):      
        '''crea il prodotto
        tags : lista di tag
        '''        
        self.nome = nome
        self.produttore = produttore
        self.prezzo = prezzo
        self.tags  = tags
        super().__init__()
    
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
            self.insertDataProdotto(dct)
        else:
            return dct
    