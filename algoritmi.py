# ----------------------------------------------------------------
# liear regression
# ----------------------------------------------------------------
from liste import prodotti,tags,prezzi,produttori
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.preprocessing import OrdinalEncoder


def preprocessing():
    df = pd.DataFrame({'prodotti':prodotti, 'produttori':produttori, 'prezzi':prezzi, 'tags':tags})
    print(df)
    oe = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    # lista di tag totali
    tag_tot = [t for x in tags for t in x]
    # ottengo ordinal encoder della lista     
    oe.fit( np.array(tag_tot).reshape(-1, 1))
    t = oe.transform( np.array(tag_tot).reshape(-1, 1))
    
    oe.fit(np.array(df['produttori']).reshape(-1, 1))
    p = oe.transform(np.array(df['produttori']).reshape(-1, 1))

    def diz_nome_codice(keys, values):
        diz = {k: int(v) for k, v in zip(keys, values)}
        return diz
    
    
    diz_prod = diz_nome_codice(df['produttori'], p)
    
    new_prod = [diz_prod[p] for p in df['produttori']]
    
    diz_tag = diz_nome_codice(tag_tot, t)
    
    new_tags = []
    for tupla in df['tags']:
        new_row = []
        for x in tupla:
            new_row.append(diz_tag[x])
        new_tags.append(new_row)
    
    df['tags'] = new_tags
    df['produttori'] = new_prod
    
    print(df)
        
    

def predicta():
    x = np.array(x).reshape(-1, 1)
    y = np.array(y).reshape(-1, 1)

    X_train, X_test, y_train, y_test = train_test_split(
        x, y, random_state=42)
    reg_bp = LinearRegression()
    reg_bp.fit(X_train, y_train)

    y_pred = reg_bp.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    

preprocessing()