# ----------------------------------------------------------------
# liear regression
# ----------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

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