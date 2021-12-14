from flask import Flask,render_template,request,session,jsonify,json
from bson import json_util
from flask_wtf import FlaskForm
from flask_pymongo import PyMongo
import pymongo
from wtforms import DateField,SelectField,SubmitField,RadioField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from pymongo import MongoClient, mongo_client
import pandas as pd
import pymongo
import getdata

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'
Bootstrap(app)
 #------------------------ อีกวิธีนึง -----------------------------------
#app.config["MONGO_URI"] = "mongodb://localhost:27017/sample1"
#mongo = PyMongo(app)
'''
mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/sample1")
db = mongodb_client.db
app.config["MONGO_URI"] = "mongodb://localhost:27017/todo_db"
mongodb_client = PyMongo(app)
db = mongodb_client.db
'''

mongoClient = MongoClient('mongodb://localhost:27017')
db = mongoClient.get_database('sample1')
data_sample = db.get_collection('database')

class Part1Form(FlaskForm):
    startdate = DateField("เริ่มต้น", validators=[DataRequired()])
    enddate = DateField("สิ้นสุด", validators=[DataRequired()])
    airport_a = SelectField('สนามบิน A', choices=[('A','A'),('B','B'),('C','C')], validators=[DataRequired()]) #choices=[(parameter,display_name)]
    airport_b = SelectField('สนามบิน B', choices=[('D','D'),('E','E'),('F','F')], validators=[DataRequired()])
    level = SelectField('ระดับ', choices=[('Hour','ชั่วโมง'),('Day','วัน')], validators=[DataRequired()])
    inout = RadioField('เข้าหรือออก', choices=[('checkin','ขาเข้า'),('checkout','ขาออก')], validators=[DataRequired()])
    submit1 = SubmitField("บันทึก")

@app.route('/', methods=["GET","POST"])
def cluster():
    form1 = Part1Form()

    session['startdate'] = False
    session['enddate'] = False
    session['airport_a'] = ""
    session['airport_b'] = ""
    session['level'] = ""
    session['inout'] = ""
    '''
    startdate = False
    enddate = False
    airport_a = False
    airport_b = False
    level = False
    inout = False
    '''

    if form1.validate_on_submit():
        session['startdate'] = form1.startdate.data
        session['enddate'] = form1.enddate.data
        session['airport_a'] = form1.airport_a.data
        session['airport_b'] = form1.airport_b.data
        session['level'] = form1.level.data
        session['inout'] = form1.inout.data

        form1.startdate.data = ""
        form1.enddate.data = ""
        form1.airport_a = ""
        form1.airport_b = ""
        form1.level = ""
        form1.inout.data = ""
        
    return render_template("part1.html", form=form1)

@app.route('/spillinfo', methods=["GET","POST"])
def spill():
    return "Hello World"

@app.route('/predictpassenger', methods=["GET","POST"])
def predict():
    return "Hello World"

@app.route('/test')
def import_db():
    '''
    #test = mongo.db.database.find({"TraffTypeDescTH": 'เที่ยวบินประจำภายในประเทศ'})
    #test = db.database.find()
    #test = mongo.db.database.find({"TraffTypeDescTH": 'เที่ยวบินประจำภายในประเทศ'})
    test = data_sample.find({"TraffTypeDescTH": 'เที่ยวบินประจำภายในประเทศ'})
    #return render_template("index.html",online_users=online_users)
    docs_list  = list(test)
    df_list = pd.DataFrame(docs_list)
    #return json.dumps(docs_list, default=json_util.default)
    print("Kuyyyyyyyyyyyyyyy", test)
    testhee = json.dumps(docs_list, default=str, ensure_ascii=False).encode('utf8')
    return testhee
    '''
    arr_test = getdata.import_data("ขาเข้า","เที่ยวบินประจำภายในประเทศ")
    return render_template('test.html', tables=[arr_test.to_html(classes='test')]
    ,titles = ['Df Test'])
    
if __name__ == "__main__":
    app.run(port=80,debug=True)