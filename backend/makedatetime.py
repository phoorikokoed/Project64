import pandas as pd
import numpy as np

def convertdatetime (df):
  #df['TRN_DD'] = df['TRN_DD'].apply(str)
  #df['TRN_MM']= df['TRN_MM'].apply(str)
  #df['TRN_YY']= df['TRN_YY'].apply(str)
  #df['TRN_TIME']= df['TRN_TIME'].apply(str)

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

  resam = df.resample('H')["PASSENGER"].sum().dropna()
  rng = pd.date_range(resam.index.min().floor('d'), resam.index.max().floor('d') + pd.Timedelta(23, unit='h'), freq='H')
  diff_idx = rng.difference(resam.index)
  data_merge = pd.concat([df, pd.DataFrame(index=diff_idx, columns=df.columns)]).sort_index()
  data_fill = data_merge.PASSENGER.fillna(0)
  data_merge_success = data_fill.resample('H').sum().dropna()
  df_merge = data_merge_success.to_frame()
  return df_merge

def convertdate(df):
  #df['TRN_DD'] = df['TRN_DD'].apply(str)
  #df['TRN_MM']= df['TRN_MM'].apply(str)
  #df['TRN_YY']= df['TRN_YY'].apply(str)
  #df['TRN_TIME']= df['TRN_TIME'].apply(str)

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

def select_time(df,start_date,end_date):
    dataframe = df.loc[start_date:end_date]
    return dataframe