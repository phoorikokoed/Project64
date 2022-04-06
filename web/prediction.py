import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import numpy as np

def plusdate(enddate):
    enddate = datetime.strptime(enddate, '%Y-%m-%d') #convert from str to datetime
    d = enddate + timedelta(days=1) # plus one day
    dateStr = d.strftime("%Y-%m-%d")
    return dateStr

def select_time(df,start_date,end_date):
    df = df.set_index('date_and_time')
    dataframe = df.loc[start_date:end_date]
    #dataframe = dataframe[dataframe.PASSENGER != 0]
    dataframe = dataframe.fillna(0)
    dataframe = dataframe.reset_index()
    return dataframe

def converttime(df):
  df['TRN_DD'] = df['TRN_DD'].apply(str)
  df['TRN_MM']= df['TRN_MM'].apply(str)
  df['TRN_YY']= df['TRN_YY'].apply(str)
  df['TRN_TIME']= df['TRN_TIME'].apply(str)

  time = []
  for i in df['TRN_TIME']:
    if len(i) == 1:
      i = "00:0" + i
    elif len(i) == 2:
      i = "00:" + i
    elif len(i) == 3:
      i = i[:1] + ":" + i[1:]
      i = "0" + i
    elif len(i) == 4:
      i = i[:2] + ":" + i[2:]
    time.append(i)

  combined = df.TRN_YY.str.cat(df.TRN_MM, sep='-')
  combined = combined.str.cat(df.TRN_DD, sep='-')
  combined = combined.str.cat(time, sep=' ')

  df['date_and_time'] = pd.to_datetime(combined)
  df.set_index('date_and_time', inplace = True)
  return df

def getdatevalue(df):
    df['Year'] = df['date_and_time'].dt.year
    df['Month'] = df['date_and_time'].dt.month
    df['Week'] = df['date_and_time'].dt.isocalendar().week
    df['Date'] = df['date_and_time'].dt.day
    df['Hour'] = df['date_and_time'].dt.hour
    df['Dayofweek'] = df['date_and_time'].dt.dayofweek
    return df

def resam(dataframe):
    test_df = dataframe.resample('3H')["PASSENGER"].sum().dropna()
    df = test_df.to_frame(name = 'PASSENGER')
    df.reset_index(inplace=True)
    return df

def getoldpassenger(df,df1,df2):
    diff = df2.Year.max() - df1.Year.max()
    if diff > 0:
      df['Previous'] = df.groupby([df['date_and_time'].dt.month,df['date_and_time'].dt.day,df['date_and_time'].dt.hour])['PASSENGER'].shift(periods = diff)
      df['2Previous'] = df.groupby([df['date_and_time'].dt.month,df['date_and_time'].dt.day,df['date_and_time'].dt.hour])['PASSENGER'].shift(periods = diff+1)
      df['3Previous'] = df.groupby([df['date_and_time'].dt.month,df['date_and_time'].dt.day,df['date_and_time'].dt.hour])['PASSENGER'].shift(periods = diff+2)
      df['4Previous'] = df.groupby([df['date_and_time'].dt.month,df['date_and_time'].dt.day,df['date_and_time'].dt.hour])['PASSENGER'].shift(periods = diff+3)
    else:
      df['Previous'] = df.groupby([df['date_and_time'].dt.month,df['date_and_time'].dt.day,df['date_and_time'].dt.hour])['PASSENGER'].shift(periods = 1)
      df['2Previous'] = df.groupby([df['date_and_time'].dt.month,df['date_and_time'].dt.day,df['date_and_time'].dt.hour])['PASSENGER'].shift(periods = 2)
      df['3Previous'] = df.groupby([df['date_and_time'].dt.month,df['date_and_time'].dt.day,df['date_and_time'].dt.hour])['PASSENGER'].shift(periods = 3)
      df['4Previous'] = df.groupby([df['date_and_time'].dt.month,df['date_and_time'].dt.day,df['date_and_time'].dt.hour])['PASSENGER'].shift(periods = 4)
    #df = df.set_index('date_and_time')
    return df

def merge(df,factor1,factor2):
    df_merge = pd.merge(df,factor1, on=['Year','Month'])
    df_merge2 = pd.merge(df_merge,factor2, on=['Year','Month','Date'],how='left')
    df = df_merge2
    df.set_index("date_and_time", inplace=True)
    return df

def randomforest(df_train,df_input,input_col):
    X = df_train[input_col].values
    y = df_train['PASSENGER'].values
    X_predict = df_input[input_col].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    regr = RandomForestRegressor(n_estimators=100,min_samples_split=2,max_depth=100,
                             min_samples_leaf=1,max_features=len(input_col),ccp_alpha=0,n_jobs=-1)

    regr.fit(X_train, y_train)
    pred = regr.predict(X_predict)
    pred = np.floor(pred)
    df_input['Predict'] = pred
    return df_input
# def random_forest_prediction(df,factor,predict):
#     df

#     regr = RandomForestRegressor(max_depth=len(factor),
#     max_features=len(factor),random_state=42)

