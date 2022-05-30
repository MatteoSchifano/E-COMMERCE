# ----------------------------------------------------------------
# liear regression
# ----------------------------------------------------------------
from liste import prodotti,tags,prezzi,produttori
from back import Extract, GestisciProdotto

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.preprocessing import OrdinalEncoder



def preprocessing(df):
    # df = pd.DataFrame({'prodotti':prodotti, 'produttori':produttori, 'prezzi':prezzi, 'tags':tags})
    print(df)
    oe = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    # lista di tag totali
    tag_tot = [t for x in tags for t in x]
    # ottengo ordinal encoder della lista     
    oe.fit( np.array(tag_tot).reshape(-1, 1))
    t = oe.transform( np.array(tag_tot).reshape(-1, 1))
    
    oe.fit(np.array(df['produttore']).reshape(-1, 1))
    p = oe.transform(np.array(df['produttore']).reshape(-1, 1))

    def diz_nome_codice(keys, values):
        diz = {k: int(v) for k, v in zip(keys, values)}
        return diz
    
    
    diz_prod = diz_nome_codice(df['produttore'], p)
    
    new_prod = [diz_prod[p] for p in df['produttore']]
    
    diz_tag = diz_nome_codice(tag_tot, t)
    
    from sklearn.preprocessing import MultiLabelBinarizer

    mlb = MultiLabelBinarizer()

    df2 = pd.DataFrame(mlb.fit_transform(df.tags),columns=mlb.classes_, index=df.index)
    
    # new_tags = []
    # for tupla in df['tags']:
    #     new_row = []
    #     for x in tupla:
    #         new_row.append(diz_tag[x])
    #     new_tags.append(new_row)
    
    # df['tags'] = new_tags
    df['produttore'] = new_prod
    df = pd.concat([df, df2], axis=1)
    del df['tags']
    del df['_id']
    del df['prezzo']
    
    return df
        
    

def predicta(df):
    from sklearn.neighbors import NearestNeighbors
    import numpy as np
    X = np.array(df.iloc[:, 1:])
    knn = NearestNeighbors(n_neighbors=3, algorithm='auto').fit(X)
    distances, indices = knn.kneighbors(X)
    print(distances, indices)

# preprocessing dati di mongo
# df = preprocessing(Extract().format())


# print (df.iloc[:, 1:])
# predicta(df)

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
print(df3.head())

dict_df = df3.to_json(orient='records')

import json
parsed = json.loads(dict_df)

GestisciProdotto().insertDataProdotto(parsed, one=False)