import pandas as pd
import numpy as np
import scipy.stats as stats
import math
from tslearn.clustering import TimeSeriesKMeans
from yellowbrick.cluster.elbow import kelbow_visualizer

def convertdata(df):
    dfvalues = df.PASSENGER.values
    df_list = [dfvalues[i:i+24] for i in range(0,len(dfvalues), 24)]
    df_mat = np.matrix(df_list, dtype=np.float)
    df_arr = np.array(df_list)

    return df_arr

def countday(df):
  mon,tue,wed,thu,fri,sat,sun = 0,0,0,0,0,0,0
  cluster = np.unique(df.cluster)[0]
  for i in range(len(df)):
    day = df.index[i].weekday()
    if day == 0:
      mon += 1
    elif day == 1:
      tue += 1
    elif day == 2:
      wed += 1
    elif day == 3:
      thu += 1
    elif day == 4:
      fri += 1
    elif day == 5:
      sat += 1
    else:
      sun += 1
  #print(f'Cluster : {cluster}\nIn {len(df)} day(s) consist of\nSunday : {sun} day(s)\nMonday : {mon} day(s)\nTuesday : {tue} day(s)\nWednesday : {wed} day(s)\nThursday : {thu} day(s)\nFriday : {fri} day(s)\nSaturday : {sat} day(s)\n=============================')

def dtw_clustering(arr, cluster):
  seed = 0
  np.random.seed(seed)
  cluster_count = cluster #Test this is a summer

  kmeans_summer = TimeSeriesKMeans(n_clusters = cluster_count, 
  metric='dtw', 
  max_iter=100, 
  random_state=seed, 
  dtw_inertia=True)
  kmeans_summer.fit(arr)
  y_pred_summer = kmeans_summer.predict(arr)

  return y_pred_summer

def create_dataframe(ori_df,array,pred):
  s = np.unique(ori_df.index.date)
  df_ans = pd.DataFrame(array)
  df_ans['Cluster'] = pred
  df_ans.set_index([s], inplace = True)

  return df_ans

def create_df(ori_df,array,pred):
  s = np.unique(ori_df.index.date)
  df = pd.DataFrame({'date' : [], 'Passenger': [], 'Cluster': []})
  for i in range(len(array)):
    data = {'date': s[i],
    'Passenger': array[i],
    'Cluster': pred[i]}
    dataframe = pd.DataFrame(data=data)
    df = pd.concat([df, dataframe])
  df = df.reset_index().rename(columns={df.index.name:'hour'})
    #df.drop(['level_0'], axis=1, inplace = True)
  return df

def calculate_mean(df):
  hour = [10,15,18]
  df_answer = [[k for k in df.Cluster.unique()]]
  #df_answer = []
  for j in hour:
      answer = []
      for i in df.Cluster.unique():
          answer.append(round(df[(df['Cluster']==i) & (df['index']==j)].Passenger.mean(),3))
      df_answer.append(answer)
  return df_answer

def get_k_value(array):
  seed = 0
  np.random.seed(seed)
  model = TimeSeriesKMeans(metric='dtw', max_iter=100, random_state=seed, dtw_inertia=True)
  a = kelbow_visualizer(model, X = array, k=(3, 10), timings=False, show=False)
  k = a.elbow_value_
  return k
