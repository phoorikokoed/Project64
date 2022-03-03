import pandas as pd
from datetime import datetime
from sklearn.preprocessing import StandardScaler

def getdatevalue(df):
    df['Year'] = df['DateTime'].dt.year
    df['Month'] = df['DateTime'].dt.month
    df['Week'] = df['DateTime'].dt.isocalendar().week
    df['Date'] = df['DateTime'].dt.day
    df['Hour'] = df['DateTime'].dt.hour
    df['Dayofweek'] = df['DateTime'].dt.dayofweek
    return df