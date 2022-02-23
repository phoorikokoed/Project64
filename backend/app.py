from cgi import test
from flask import Flask,render_template,request,session,jsonify,json
from bson import json_util
from flask_wtf import FlaskForm
from flask_pymongo import PyMongo
import json
from matplotlib.font_manager import json_dump
from wtforms import DateField,SelectField,SubmitField,RadioField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from pymongo import MongoClient, mongo_client
import pandas as pd
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from plotly.graph_objs import FigureWidget
from datetime import datetime
import getdata, makedatetime, capacity_insert, spill_f, clustering

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'
Bootstrap(app)

mongoClient = MongoClient('mongodb://localhost:27017')

data_in = getdata.import_data("ขาเข้า")
data_test = getdata.import_data("ขาเข้า")

@app.route('/')
def home():
    
    return render_template("home.html")

@app.route('/clustering', methods=["GET","POST"])
def cluster():        
    return render_template("part1_test.html")

@app.route('/displaypart1', methods=["GET","POST"])
def display1():
    if request.method == 'POST':
        date = request.form['date'] #This is a str type
        enddate = request.form['enddate'] #This is a str type
        inout = request.form['inout']

    data = data_test

    df = makedatetime.convertdatetime(data)
    df = df.sort_index()
    df_period = makedatetime.select_time(df,date,enddate)

    arr = clustering.convertdata(df_period)
    #cluster = clustering.get_k_value(arr)
    cluster = 4
    prediction = clustering.dtw_clustering(arr, cluster)
    df_ans = clustering.create_dataframe(df_period,arr,prediction)

    df_ans_test = clustering.create_df(df_period,arr,prediction)
    df_ans_test = df_ans_test.sort_values(by=['Cluster', 'date', 'index'])

    df_table = clustering.calculate_mean(df_ans_test)
    #f_cluster = df_ans_test[df_ans_test.Cluster == 1]
    
    fig = px.line(data_frame = df_ans_test, 
    x = 'index', 
    y = 'Passenger', 
    color='date',
    facet_row = 'Cluster',labels={"index": "Hours"})
    
    fig.update_layout(height=850,width=1600,showlegend=False, modebar_remove=True,title_text=f"Clustering {date} to {enddate}",title_x=0.5)
    fig.add_trace(go.Table(
    #columnorder = [1,2,3,4],
    #margin=dict(l=5,r=5,b=10,t=10),
    domain=dict(x=[0,0.23]),
    columnwidth = [5,5,5,5],
    header = dict(height = 30,
                  values = [['<b>Cluster</b>'],['<b>เช้า</b>'],
                            ['<b>บ่าย</b>'], ['<b>เย็น</b>']],
                  line = dict(color='rgb(50, 50, 50)'),
                  align = ['left'] * 5,
                  font = dict(color=['rgb(45, 45, 45)'] * 5, size=14),
                  fill = dict(color='#d562be')),
    cells = dict(values = [k for k in df_table],
                 line = dict(color='#506784'),
                 align = ['left'] * 5,
                 height = 25,
                 fill = dict(color=['rgb(235, 193, 238)', 'rgba(228, 222, 249, 0.65)']))
    ))
    fig.update_layout(margin=dict(b=20,t=30))
    #fig_test = go.FigureWidget(data=[fig1]) 
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    #fig_test = plotly.io.to_json(fig1)
    return render_template("plotly_part1.html", graphJSON=graphJSON)
    #return df_ans_test.to_html()

@app.route('/spillinfo', methods=["GET","POST"])
def spill():
    return render_template("part2.html")

@app.route('/displaypart2', methods=["GET", "POST"])
def display2():
    if request.method == 'POST':
        #test_type = request.form['type'] #This is a str type
        startdate = request.form['startdate'] #This is a str type
        enddate = request.form['enddate'] #This is a str type

    #data_test = getdata.import_data("ขาเข้า")
    
    #data_test = data_in
    df_test = makedatetime.convertdate(data_test)
    df_test = df_test.sort_index()
    test_df = makedatetime.select_time(df_test,startdate,enddate)

    test_df['AIR_TYPE'] = test_df.apply(lambda row: capacity_insert.format_airtype(row), axis=1)
    test_df['Capacity'] = test_df.apply(lambda row: capacity_insert.insert_cap(row), axis=1)
    
    k_factor, test_k, time = spill_f.split_dataframe(test_df) #for K-factor Graph
    print(time)
    new_df = test_k[time-1].explode(['Demand', 'Demand_Factor(D)', 'Load_Factor(L)', 'Spill_Factor(S)', 'Spill', 'Spill as % of demand'])
    new_df_test = new_df.reset_index()
    #for i in range(time):
    new_df_test["Time"] = new_df_test["index"].replace({0: "06:00 - 11:00", 
    1: "11:00 - 15:00",
    2: "15:00 - 19:00",
    3: "19:00 - 23:00",
    4: "23:00 - 06:00",
    })

    df_chart = spill_f.resample_df(test_df)
    df_chart = makedatetime.select_time(df_chart, startdate, enddate)
    df_chart['date'] = [date.strftime("%Y-%m-%d") for date in df_chart.index.date]
    df_chart = df_chart.reset_index()
    df_chart = df_chart[df_chart.Passenger != 0]

    fig = px.line(data_frame = new_df_test, 
    x = 'Load_Factor(L)', 
    y = 'Spill as % of demand', 
    color='Time')
    #fig.update_layout(showlegend=False, modebar_remove=True)
    fig.update_layout(
    showlegend=True, modebar_remove=True,legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01),title_text=f"K-Factor from {startdate} to {enddate}",title_x=0.5)

    fig1 = px.bar(data_frame = df_chart,
    x = 'date_and_time',
    y = 'Passenger',labels={"date_and_time": "Date&Time"})

    fig1.add_scatter(x = df_chart['date_and_time'],
    y = df_chart['Capacity'],
    mode="markers",
    fillcolor = "red",
    name = "Capacity")

    label_date = df_chart.date.unique()

    fig1.update_layout(showlegend=False, title_text=f"Graph from {startdate} to {enddate}",title_x=0.5)

    fig1.update_xaxes(type="date",calendar="thai",autorange=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    #graphJSON1 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    #return render_template("plotly_part2.html", graphJSON = graphJSON1)
    return render_template("plotly_part2.html",
    k_factor = k_factor,
    label_date = label_date, 
    graphJSON = graphJSON, 
    graphJSON1 = graphJSON1)
    
    #return df_chart.to_html()

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    #return update_graph(request.args.get('data'))
    #if request.method == 'POST':
        #test = request.form['test']
    start_date = request.args.get('data') #This is a str type
        #end_date = request.form['end_date'] #This is a str type
    end_date = request.args.get('data1')
    #2019-04-02
    #print('===============',type(test), start_date,end_date)
    return update_graph(start_date,end_date)
    
def update_graph(startdate,enddate):

    df_test = makedatetime.convertdate(data_test)
    df_test = df_test.sort_index()
    test_df = makedatetime.select_time(df_test,startdate,enddate)

    test_df['AIR_TYPE'] = test_df.apply(lambda row: capacity_insert.format_airtype(row), axis=1)
    test_df['Capacity'] = test_df.apply(lambda row: capacity_insert.insert_cap(row), axis=1)

    df_chart = spill_f.resample_df(test_df)
    df_chart = makedatetime.select_time(df_chart, startdate, enddate)
    df_chart['date'] = [date.strftime("%Y-%m-%d") for date in df_chart.index.date]
    df_chart = df_chart.reset_index()
    df_chart = df_chart[df_chart.Passenger != 0]

    fig1 = px.bar(data_frame = df_chart,
    x = 'date_and_time',
    y = 'Passenger',labels={"date_and_time": "Date&Time"})

    fig1.update_layout(showlegend=False, title_text=f"Graph from {startdate} to {enddate}",title_x=0.5)

    fig1.add_scatter(x = df_chart['date_and_time'],
    y = df_chart['Capacity'],
    mode="markers",
    fillcolor = "red",
    name = "Capacity")

    fig1.update_xaxes(type="date")

    graphJSON2 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON2

@app.route('/predictpassenger', methods=["GET","POST"])
def predict():
    #return "Hello World"
    return render_template("part3.html")

@app.route('/test', methods=["GET","POST"])
def import_db():
    data_test = None
    #print(type(data_test))
    data_test = getdata.import_data("ขาเข้า")
    #print(data_test['PASSENGER'][0])
    print('================================')

    df_test = makedatetime.convertdatetime(data_test)
    #print(pd.)
    #print(type(df_test.index))
    #return df_test.to_html()
    return render_template('chart.html', 
    data_chart = df_test['PASSENGER'][8:14])
    #data_index = df_test[8:14].index())

if __name__ == "__main__":
    app.run(port=80,debug=True)