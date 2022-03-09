from flask import json
from pymongo import MongoClient
import pandas as pd

mongoClient = MongoClient('mongodb://localhost:27017')
db = mongoClient.get_database('sample1')
data_sample = db.get_collection('data')

factor = db.get_collection('factor')
factor_date = db.get_collection('factor_date')

def import_data(groups):
    test = data_sample.find({"ARR_DEP (groups)": groups})
    docs_list  = list(test)
    df_list = pd.DataFrame(docs_list)
    #df_list.rename(columns={"AirportNameTH.1": "AirportNameTH_O","ARR_DEP (groups)" : "ARR_DEP_Groups"},inplace =True)
    df = df_list.drop([
    '_id',
    'FLIGHT_NO', 
    'PORT_NAME',
    'Country Airline',
    'CITY',
    'Destination Country',
    'จำนวนนับของ ARR_DEP (groups)',
    'PASSENGER_TRANSFER',
    'PASSENGER_TRANSIT',
    'FREIGHT',
    'TRAFF_TYPE',
    'CARD_NO'],
     axis=1)

    dff = df[(df.TraffTypeDescTH == 'เที่ยวบินประจำภายในประเทศ')]
    dft = dff[((dff.AirportNameTH_O == 'ท่าอากาศยานดอนเมือง') | (dff.AirportNameTH_O == 'ท่าอากาศยานสุวรรณภูมิ'))]
    # dft = dff[(dff.AirportNameTH == 'ท่าอากาศยานกระบี่') & 
    # ((dff.AirportNameTH_O == 'ท่าอากาศยานดอนเมือง') | (dff.AirportNameTH_O == 'ท่าอากาศยานสุวรรณภูมิ'))]
    #dft = dft.astype({"TRN_DD": int})
    dft = dft.sort_values(["TRN_YY","TRN_MM", "TRN_DD","TRN_TIME"], ascending = (True,True,True,True))
    
    return dft