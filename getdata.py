from flask import json
from pymongo import MongoClient
import pandas as pd

mongoClient = MongoClient('mongodb://localhost:27017')
db = mongoClient.get_database('sample1')
data_sample = db.get_collection('database')

def import_data(groups,trafftype):
        test = data_sample.find({"ARR_DEP (groups)": groups ,"TraffTypeDescTH": trafftype})
        docs_list  = list(test)
        df_list = pd.DataFrame(docs_list)
        df_list.rename(columns={"AirportNameTH.1": "AirportNameTH_O","ARR_DEP (groups)" : "ARR_DEP_Groups"},inplace =True)
        df = df_list.drop(['_id','FLIGHT_NO', 'PORT_NAME','Country Airline','CITY','Destination Country','จำนวนนับของ ARR_DEP (groups)','PASSENGER_TRANSFER','PASSENGER_TRANSIT','FREIGHT','TRAFF_TYPE','CARD_NO'], axis=1)
        #sample_list = list(df)
        sam_data = json.dumps(df, default=str, ensure_ascii=False).encode('utf8')
        print(type(sam_data))
        return df

'''
if __name__ == "__main__":
    main()
'''