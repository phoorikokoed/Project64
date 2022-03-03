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
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import getdata, makedatetime, capacity_insert, spill_f, clustering, prediction

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'
Bootstrap(app)

mongoClient = MongoClient('mongodb://localhost:27017')

data_in = getdata.import_data("ขาเข้า")
data_out = getdata.import_data("ขาออก")

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
        inout_p1 = request.form['inout']

    print('==============', inout_p1)
    if inout_p1 == "Arrival":
        data = data_in
    else:
        data = data_out

    df = makedatetime.convertdatetime(data)
    df = df.sort_index()
    df_period = makedatetime.select_time(df,date,enddate)

    arr = clustering.convertdata(df_period)
    #cluster = int(clustering.get_k_value(arr))
    cluster = 4
    prediction = clustering.dtw_clustering(arr, cluster)
    prediction += 1
    df_ans = clustering.create_dataframe(df_period,arr,prediction)

    df_ans_test = clustering.create_df(df_period,arr,prediction)
    df_ans_test = df_ans_test.sort_values(by=['Cluster', 'date', 'index'])

    df_table = clustering.calculate_mean(df_ans_test)
    #f_cluster = df_ans_test[df_ans_test.Cluster == 1]
    
    '''
    fig = px.line(data_frame = df_ans_test, 
    x = 'index', 
    y = 'Passenger', 
    color='date',
    facet_row = 'Cluster',labels={"index": "Hours"})
    '''
    #Craeate Variable for config graph title and specs
    title = ['Cluster 1:', 'Passengers:']
    a = [f'Cluster {i}:' for i in range(2,cluster+1)]
    title.extend(a)

    spec = [[{"type": "xy"}, {"type": "table","rowspan": cluster}]]
    b = [[{"type": "xy"}, None]]*(cluster-1)
    spec.extend(b)

    fig = make_subplots(rows=cluster, cols=2, subplot_titles=(title),vertical_spacing = 0.075,
    specs=spec,column_widths=[0.85, 0.15])

    for i in range(1,cluster+1):
        # Add traces
        fig2 = px.line(data_frame = df_ans_test[df_ans_test.Cluster == i], 
        x = 'index', 
        y = 'Passenger', 
        color='date',
        labels={"index": "Hours"})
        for j in range(len(fig2['data'])):
            fig.add_trace(fig2['data'][j], row=i, col=1)
        fig.update_layout(height=cluster*300)
        fig.update_xaxes(title_text="Hours", title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'),row=i, col=1)
        fig.update_yaxes(title_text="Passengers", title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'),row=i, col=1, range=[-50, df_ans_test.Passenger.max()+70])
        fig.layout.annotations[i-1].update(x=0.04,font=dict(size=18,color='Black',family='Open Sans, monospace'))
    fig.layout.annotations[cluster].update(x=0.04,font=dict(size=18,color='Black',family='Open Sans, monospace'))
    fig.layout.annotations[1].update(x=0.83,font=dict(size=18,color='Black',family='Open Sans, monospace'))

    fig.update_layout(autosize=True,showlegend=False, modebar_remove=True,title_text=f"Group's Result from {date} to {enddate} | {inout_p1}",title_x=0.5,
    font=dict(size=14,color="Black",family='Open Sans, monospace'),
    hoverlabel=dict(bgcolor="white",font_size=16))
    
    fig.add_trace(go.Table(

    domain=dict(x=[0,0.023]),
    columnwidth = [5,5,5,5],
    header = dict(height = 30,
                  values = [['<b>Cluster</b>'],['<b>10:00</b>'],
                            ['<b>15:00</b>'], ['<b>18:00</b>']],
                  line = dict(color='rgb(50, 50, 50)'),
                  align = ['left'] * 5,
                  font = dict(color=['rgb(45, 45, 45)'] * 5, size=16, family='Open Sans, monospace'),
                  fill = dict(color='#E5ECF6')),
    cells = dict(values = [k for k in df_table],
                 line = dict(color='black'),
                 align = ['left'] * 5,
                 height = 30,font = dict(color=['rgb(45, 45, 45)'] * 5, size=16, family='Open Sans, monospace'),
                 fill = dict(color=['#E3F2FD', 'white']))
    ),row=1, col=2)
    fig.update_traces(domain_x=[0.8,1], selector=dict(type='table'))


    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("plotly_part1.html", graphJSON=graphJSON, table=df_table)
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
        inout_p2 = request.form['inout']

    print('==============', inout_p2)
    if inout_p2 == "Arrival":
        data_test = data_in
    else:
        data_test = data_out

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
    new_df_test["Time"] = new_df_test["index"].replace({0: f"06:00 - 11:00 : {round(k_factor[0],3)}" , 
    1: f"11:00 - 15:00 : {round(k_factor[1],3)}",
    2: f"15:00 - 19:00 : {round(k_factor[2],3)}",
    3: f"19:00 - 23:00 : {round(k_factor[3],3)}",
    4: f"23:00 - 06:00 : {round(k_factor[4],3)}",
    })

    df_chart = spill_f.resample_df(test_df)
    df_chart = makedatetime.select_time(df_chart, startdate, enddate)
    df_chart['date'] = [date.strftime("%Y-%m-%d") for date in df_chart.index.date]
    df_chart = df_chart.reset_index()
    df_chart = df_chart[df_chart.Passenger != 0]
    df_chart['Diff'] = df_chart['Capacity'] - df_chart['Passenger']

    fig = px.line(data_frame = new_df_test, 
    x = 'Load_Factor(L)', 
    y = 'Spill as % of demand', 
    color='Time')

    fig.update_layout(
    showlegend=True, modebar_remove=True,hovermode='closest',
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    font=dict(size=14,color="Black",family='Open Sans, monospace'),
    hoverlabel=dict(bgcolor="white",font_size=16),
    title_text=f"K-Factor from {startdate} to {enddate} | {inout_p2}",title_x=0.5)
    fig.update_xaxes(title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    fig.update_yaxes(title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    '''
    fig1 = px.bar(data_frame = df_chart,
    x = 'date_and_time',
    y = 'Passenger',labels={"date_and_time": "Date&Time"})

    fig1.add_scatter(x = df_chart['date_and_time'],
    y = df_chart['Capacity'],
    mode="markers",
    fillcolor = "red",
    name = "Capacity")
    '''
    fig1 = go.Figure(data=[
        go.Bar(name='Passenger', x=df_chart['date_and_time'], y=df_chart['Passenger'],marker_color='mediumseagreen'),
        go.Bar(name='Capacity', x=df_chart['date_and_time'], y=df_chart['Diff'],marker_color='red')
    ])

    label_date = df_chart.date.unique()

    fig1.update_layout(showlegend=True, title_text=f"Krabi's Results from {startdate} to {enddate} | {inout_p2}",title_x=0.5, barmode='stack',
    xaxis_title="Time",yaxis_title="Passenger",
    font=dict(size=14,color="Black",family='Open Sans, monospace'),
    legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
 
    fig1.update_xaxes(type="date", range=[startdate,label_date[2]], rangemode='normal',title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    fig1.update_yaxes(title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("plotly_part2.html",
    k_factor = k_factor,
    label_date = label_date, 
    graphJSON = graphJSON, 
    graphJSON1 = graphJSON1,
    inout_p2 = inout_p2)
    
    #return df_test.to_html()

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    #return update_graph(request.args.get('data'))
    #if request.method == 'POST':
        #test = request.form['test']
    start_date = request.args.get('data') #This is a str type
        #end_date = request.form['end_date'] #This is a str type
    end_date = request.args.get('data1')
    inout_p2 = request.args.get('data2')
    print('StartDate',start_date)
    print('Enddate is',end_date)
    print('==================',inout_p2)
    #print('===============',type(test), start_date,end_date)
    return update_graph(start_date,end_date,inout_p2)
    
def update_graph(startdate,enddate,inout_p2):

    if inout_p2 == 'Arrival':
        data_test = data_in
    else:
        data_test = data_out

    df_test = makedatetime.convertdate(data_test)
    df_test['date'] = [date.strftime("%Y-%m-%d") for date in df_test.index.date]
    df_test = df_test.sort_index()
    test_df = makedatetime.select_time(df_test,startdate,enddate)

    test_df['AIR_TYPE'] = test_df.apply(lambda row: capacity_insert.format_airtype(row), axis=1)
    test_df['Capacity'] = test_df.apply(lambda row: capacity_insert.insert_cap(row), axis=1)

    df_chart = spill_f.resample_df(test_df)
    df_chart = makedatetime.select_time(df_chart, startdate, enddate)
    df_chart['date'] = [date.strftime("%Y-%m-%d") for date in df_chart.index.date]
    df_chart = df_chart.reset_index()
    df_chart = df_chart[df_chart.Passenger != 0]
    df_chart['Diff'] = df_chart['Capacity'] - df_chart['Passenger']

    label_date = df_test.date.unique()
    
    fig1 = go.Figure(data=[
        go.Bar(name='Passenger', x=df_chart['date_and_time'], y=df_chart['Passenger'],marker_color='mediumseagreen'),
        go.Bar(name='Capacity', x=df_chart['date_and_time'], y=df_chart['Diff'],marker_color='red')
    ])


    fig1.update_layout(showlegend=True, title_text=f"Krabi's BarGraph Results from {startdate} to {enddate} | {inout_p2}",title_x=0.5, barmode='stack',
    xaxis_title="Time",yaxis_title="Passenger",
    font=dict(size=14,color="Black",family='Open Sans, monospace'),
    legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))

    fig1.update_xaxes(type="date", rangemode='normal', range=[startdate,label_date[np.where(label_date == enddate)[0][0]+1]])

    graphJSON2 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON2

@app.route('/predictpassenger', methods=["GET","POST"])
def predict():

    return render_template("part3.html")

@app.route('/displaypart3', methods=["GET", "POST"])
def modelpredict():
    if request.method == 'POST':
        startdate = request.form['startdate'] #This is a str type
        enddate = request.form['enddate'] #This is a str type
        #inout_p3 = request.form['inout']
    daterange = pd.date_range(start=startdate, end=enddate, freq ='3H')
    df_datetime = daterange.to_frame(name = 'DateTime')
    df_time = prediction.getdatevalue(df_datetime)
    #return "Hello World"
    return df_time.to_html()

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