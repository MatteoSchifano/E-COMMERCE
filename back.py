import datetime
from pymongo import MongoClient
# from liste import *
import hashlib
import pandas as pd

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

    def serchData(self, coll, qwer:dict, proj:dict = None, lim:int = None):
        '''
        restituisce una lista di dizionari corrispondenti alla qwerry
        '''
        client, col = self.connect(coll)
        if lim:
            post = list(col.find(filter=qwer, projection=proj, limit=lim))
        else:
            post = list(col.find(filter=qwer, projection=proj))
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
            ad = qwerry[0]['admin']
            self.updateDataAccess(qwerry[0])
            return True, last, ad
        else:
            return False, None, 0
            
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
        if username == 'admin':
            self.admin = 1
        else:
            self.admin = 0
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
            'lastAcc':self.lastAcc,
            'admin':self.admin
        }
        if ins == True:
            self.insertDataUtente(dct)
        else:
            return dct

class GestisciProdotto(MainDb):

    coll='prodotto'

    def serchDataProdotto(self, qwer: dict, proj: dict = None, lim: int = None):
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

class Extract(GestisciProdotto):
    
    def format(self):
        '''
        estrae tutto il database e restituisce un dataframe
        '''
        lst = self.estrai()
        return pd.DataFrame.from_dict(lst, orient='columns')

class Carrello(GestisciProdotto):

    lst = []

    def __init__(self) -> None:
        pass

    def aggACarrello(self,**kargs):
        self.lst.append(**kargs)
        return self.lst

    def correlati(self, lung:int = 5):
        idprod = self.lst[-1]['_id']
        correlati = CorreletedProduct(df=Extract().format()).consiglia_prodotti(idprod)
        cor = correlati[0:lung]
        lista = []
        for el in cor:
            lista.append(self.serchDataProdotto({'_id':el}))
        return lista

# ===============================================================
import numpy as np
import pandas as pd

import ast



from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import StandardScaler
class CorreletedProduct():

    def __init__(self, df = Extract().format(), target:dict=None):
        self.df     = self.preprocessing(df)
        self.target = target

    def __modella_csv():
        '''TODO da eliminare'''
        df = pd.read_csv('Product.csv')

        # utilizziamo le colonne strettamente necessarie
        nomi = df.iloc[:, 1]
        produttori = df.iloc[:, 9]
        prezzi = df.iloc[:, -1]
        tags = df.iloc[:, -4:-1]
        # unione dei tags
        tags = tags[tags.columns[:]].apply(
            lambda x: ','.join(x.dropna().astype(str)),
            axis=1)

        # concatenazione dei diversi dataframe e rinomina delle colonne
        df3 = pd.concat([nomi, produttori, prezzi, tags], axis=1)
        df3.columns = ['nome', 'produttore', 'prezzo', 'tags']

        df3.dropna()

        dict_df = df3.to_json(orient='records')

        import json
        parsed = json.loads(dict_df)

        GestisciProdotto().insertDataProdotto(parsed, one=False)


    def preprocessing(self, df):
        # permette di la divisione dei tags
        df.tags = df.tags.str[1:-1].str.split(',').tolist()

        oe = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
        oe.fit(np.array(df['produttore']).reshape(-1, 1))
        p = oe.transform(np.array(df['produttore']).reshape(-1, 1))

        def diz_nome_codice(keys, values):
            diz = {k: int(v) for k, v in zip(keys, values)}
            return diz

        diz_prod = diz_nome_codice(df['produttore'], p)
        new_prod = [diz_prod[p] for p in df['produttore']]
        df['produttore'] = new_prod


        mlb = MultiLabelBinarizer()

        df2 = pd.DataFrame(mlb.fit_transform(df.tags),
                        columns=mlb.classes_, index=df.index)

        scaler = StandardScaler()
        # transform data
        df['prezzo'] = scaler.fit_transform(df['prezzo'].values.reshape(-1, 1))

        df = pd.concat([df, df2], axis=1)
        del df['tags']
        df = df.dropna()
        return df


    def predicta(self, df):
        X = np.array(df.iloc[:, 2:])
        knn = NearestNeighbors(n_neighbors=5, algorithm='auto').fit(X)
        distances, indices = knn.kneighbors(X)
        return distances, indices


    def prodotti_correlati(self, prodotto):
        _, indices = self.predicta(self.df)

        self.target = ast.literal_eval(prodotto)
        prodotto_acquistato = self.df.loc[self.df['_id'] == self.target['_id']]
        for x in indices:
            if x[0] == prodotto_acquistato.index[0]:
                ls = [self.df.iloc[y, 0] for y in x[1:]]

        return ls

    def consiglia_prodotti(self, carrello):
        '''funzione che consiglia altri prodotti

        :param ObjectID carrello: _ID DEL PRODOTTO
        '''    
        # preprocessing dati di mongo
        ls_prodotti_correlati = self.prodotti_correlati(self.df, carrello)
        return ls_prodotti_correlati