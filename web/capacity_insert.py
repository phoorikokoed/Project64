import pandas as pd
import numpy as np

def insert_cap(df):
    #Airbus
    if df['AIR_TYPE'] == 'A300' or df['AIR_TYPE'][0:4] == 'A300':
        return 361
    elif df['AIR_TYPE'] == 'A310' or df['AIR_TYPE'][0:4] == 'A310':
        return 279
    elif df['AIR_TYPE'] == 'A318' or df['AIR_TYPE'][0:4] == 'A318':
        return 132
    elif df['AIR_TYPE'] == 'A319' or df['AIR_TYPE'][0:4] == 'A319':
        return 156
    elif df['AIR_TYPE'] == 'A320' or df['AIR_TYPE'][0:4] == 'A320':
        return 186
    elif df['AIR_TYPE'] == 'A321' or df['AIR_TYPE'][0:4] == 'A321':
        return 240
    elif df['AIR_TYPE'] == 'A330':
        return 406
    elif df['AIR_TYPE'][0:4] == 'A332' or df['AIR_TYPE'][0:6] == 'A330-2':
        return 406
    elif df['AIR_TYPE'][0:4] == 'A333' or df['AIR_TYPE'][0:6] == 'A330-3':
        return 440
    elif df['AIR_TYPE'][0:4] == 'A342' or df['AIR_TYPE'][0:6] == 'A340-2':
        return 250
    elif df['AIR_TYPE'][0:4] == 'A343' or df['AIR_TYPE'][0:6] == 'A340-3':
        return 290
    elif df['AIR_TYPE'][0:4] == 'A345' or df['AIR_TYPE'][0:6] == 'A340-5':
        return 310
    elif df['AIR_TYPE'][0:4] == 'A346' or df['AIR_TYPE'][0:6] == 'A340-6':
        return 370
    elif df['AIR_TYPE'] == 'A350' or df['AIR_TYPE'][0:4] == 'A350':
        return 475
    elif df['AIR_TYPE'] == 'A380' or df['AIR_TYPE'][0:4] == 'A380':
        return 853
    #========================================================================================================================
    #Boeing
    elif df['AIR_TYPE'] == 'B733' or df['AIR_TYPE'][0:6] == 'B737-3':
        return 149
    elif df['AIR_TYPE'] == 'B734' or df['AIR_TYPE'][0:6] == 'B737-4':
        return 168
    elif df['AIR_TYPE'] == 'B735' or df['AIR_TYPE'][0:6] == 'B737-5':
        return 132
    elif df['AIR_TYPE'] == 'B736' or df['AIR_TYPE'][0:6] == 'B737-6':
        return 132
    elif df['AIR_TYPE'] == 'B737' or df['AIR_TYPE'][0:6] == 'B737-7':
        return 149
    elif df['AIR_TYPE'] == 'B738' or df['AIR_TYPE'][0:6] == 'B737-8':
        return 189
    elif df['AIR_TYPE'] == 'B739' or df['AIR_TYPE'][0:6] == 'B737-9':
        return 220
    elif 'MAX7' in df['AIR_TYPE'] or df['AIR_TYPE'] == 'B37M':
        return 172
    elif 'MAX8' in df['AIR_TYPE'] or df['AIR_TYPE'] == 'B38M':
        return 210
    elif 'MAX9' in df['AIR_TYPE'] or df['AIR_TYPE'] == 'B39M':
        return 220
    elif 'MAX10' in df['AIR_TYPE']:
        return 230
    elif (df['AIR_TYPE'] == 'B772' or df['AIR_TYPE'][0:6] == 'B777-2') and 'LR' in df['AIR_TYPE']:
        return 317
    elif (df['AIR_TYPE'] == 'B772' or df['AIR_TYPE'][0:6] == 'B777-2') and 'ER' in df['AIR_TYPE']:
        return 313
    elif (df['AIR_TYPE'] == 'B772' or df['AIR_TYPE'][0:6] == 'B777-2') and 'ER' not in df['AIR_TYPE'] and 'LR' not in df['AIR_TYPE']:
        return 313
    elif df['AIR_TYPE'] == 'B773' or df['AIR_TYPE'][0:6] == 'B777-3':
        return 396
    elif (df['AIR_TYPE'] == 'B777F' or df['AIR_TYPE'][0:6] == 'B777-2') and (('200F' or 'F') in df['AIR_TYPE']):
        return 317
    #=========================================================================================================================
    #ATR
    elif df['AIR_TYPE'][0:4] == 'ATR4' or df['AIR_TYPE'][0:4] == 'AT-4' or df['AIR_TYPE'][0:5] == 'ATR 4':
        return 48
    elif df['AIR_TYPE'][0:4] == 'ATR7' or df['AIR_TYPE'][0:4] == 'AT-7' or df['AIR_TYPE'][0:5] == 'ATR 7':
        return 70

def format_airtype(df):
    if df['AIR_TYPE'][1] == '-':
        return df['AIR_TYPE'][:1] + df['AIR_TYPE'][1+1:]

    elif (df['AIR_TYPE'][0:3] == 'ATR' and df['AIR_TYPE'][3] == '-'):
        return df['AIR_TYPE'][:3] + df['AIR_TYPE'][3+1:]
    
    else:
        return df['AIR_TYPE']

# 'ท่าอากาศยานระนอง', 'ท่าอากาศยานกระบี่', 'ท่าอากาศยานสุราษฎร์ธานี',
#        'ท่าอากาศยานหัวหิน', 'ท่าอากาศยานชุมพร', 'ท่าอากาศยานนครราชสีมา',
#        'ท่าอากาศยานน่านนคร', 'ท่าอากาศยานบุรีรัมย์',
#        'ท่าอากาศยานร้อยเอ็ด', 'ท่าอากาศยานสกลนคร',
#        'ท่าอากาศยานอุบลราชธานี', 'ท่าอากาศยานพิษณุโลก',
#        'ท่าอากาศยานเพชรบูรณ์', 'ท่าอากาศยานเลย', 'ท่าอากาศยานแพร่',
#        'ท่าอากาศยานแม่สอด', 'ท่าอากาศยานแม่ฮ่องสอน', 'ท่าอากาศยานขอนแก่น',
#        'ท่าอากาศยานตรัง', 'ท่าอากาศยานนครพนม', 'ท่าอากาศยานนครศรีธรรมราช',
#        'ท่าอากาศยานนราธิวาส', 'ท่าอากาศยานปาย', 'ท่าอากาศยานลำปาง',
#        'ท่าอากาศยานอุดรธานี', 'ท่าอากาศยานแม่สะเรียง',
#        'ท่าอากาศยานปัตตานี', nan, 'ท่าอากาศยานตาก'
def format_airport(airport):
    if airport == 'ท่าอากาศยานระนอง':
        airport = 'Ranong Airport'
    elif airport == 'ท่าอากาศยานกระบี่':
        airport = 'Krabi International Airport'
    elif airport == 'ท่าอากาศยานสุราษฎร์ธานี':
        airport = 'Surat Thani International Airport'
    elif airport == 'ท่าอากาศยานหัวหิน':
        airport = 'Department of Civil Aviation'
    # elif airport == 'ท่าอากาศยานชุมพร':
    #     airport = ''
    # elif airport == 'ท่าอากาศยานนครราชสีมา':
    #     airport = ''
    # elif airport == 'ท่าอากาศยานน่านนคร':
    #     airport = ''
    # elif airport == 'ท่าอากาศยานบุรีรัมย์':
    #     airport = ''
    # elif airport == 'ท่าอากาศยานร้อยเอ็ด':
    #     airport = ''
    # elif airport == 'ท่าอากาศยานสกลนคร':
    #     airport = ''
    # elif airport == 'ท่าอากาศยานอุบลราชธานี':
    #     airport = ''
    # elif airport == 'ท่าอากาศยานพิษณุโลก':
    #     airport = ''
    return airport