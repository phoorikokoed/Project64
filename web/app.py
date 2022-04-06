from cgi import test
from flask import Flask,render_template,request,session,jsonify,json,session,redirect,url_for
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
db = mongoClient.get_database('sample1')


data_in = getdata.import_data("ขาเข้า")
data_out = getdata.import_data("ขาออก")
ori_data = pd.concat([data_in, data_out], ignore_index=True)
airport = ori_data.AirportNameTH.unique() 
airport = ['ท่าอากาศยานกระบี่','ท่าอากาศยานสุราษฎร์ธานี']

@app.route('/')
def home():

    return render_template("home.html")
#============================================================================ Part1 =========================================================================
@app.route('/clustering', methods=["GET","POST"])
def cluster():

    return render_template("part1_test.html", airport = airport)

@app.route('/displaypart1', methods=["GET","POST"])
def display1():
    if request.method == 'POST':
        date = request.form['date'] #This is a str type
        enddate = request.form['enddate'] #This is a str type
        inout_p1 = request.form['inout']
        airport_data1 = request.form['airport_data']

    print('==============', inout_p1)
    if inout_p1 == "Arrival":
        data = data_in
    else:
        data = data_out
    data = data[data.AirportNameTH == airport_data1]

    airport_name = capacity_insert.format_airport(airport_data1)
    df = makedatetime.convertdatetime(data)
    df = df.sort_index()
    df_period = makedatetime.select_time(df,date,enddate)

    arr = clustering.convertdata(df_period)
    cluster = int(clustering.get_k_value(arr))
    #cluster = 4
    prediction = clustering.dtw_clustering(arr, cluster)
    prediction += 1
    df_ans = clustering.create_dataframe(df_period,arr,prediction)

    df_ans_test = clustering.create_df(df_period,arr,prediction)
    df_ans_test = df_ans_test.sort_values(by=['Cluster', 'date', 'index'])

    for i in range(1,cluster+1):
        clustering.countday(df_ans[df_ans.Cluster == i])

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

    fig.update_layout(autosize=True,showlegend=False, modebar_remove=True,title_text=f"{airport_name}'s group result from {date} to {enddate} | {inout_p1}",title_x=0.5,
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
    #return data.to_html()

#============================================================================ Part2 =========================================================================
@app.route('/spillinfo', methods=["GET","POST"])
def spill():
    return render_template("part2.html", airport = airport)

@app.route('/displaypart2', methods=["GET", "POST"])
def display2():
    if request.method == 'POST':
        #test_type = request.form['type'] #This is a str type
        startdate = request.form['startdate'] #This is a str type
        enddate = request.form['enddate'] #This is a str type
        inout_p2 = request.form['inout']
        airport_data2 = request.form['airport_data']

    print('==============', inout_p2)
    if inout_p2 == "Arrival":
        data_test = data_in
    else:
        data_test = data_out

    airport_name = capacity_insert.format_airport(airport_data2)
    #data_test = getdata.import_data("ขาเข้า")
    
    #data_test = data_in
    data_test = data_test[data_test.AirportNameTH == airport_data2]
    df_test = makedatetime.convertdate(data_test)
    df_test = df_test.sort_index()
    test_df = makedatetime.select_time(df_test,startdate,enddate)
    test_df = test_df.dropna()
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
    color='Time',height=600)

    fig.update_layout(
    showlegend=True, modebar_remove=True,hovermode='closest',
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    font=dict(size=14,color="Black",family='Open Sans, monospace'),
    hoverlabel=dict(bgcolor="white",font_size=16),
    title_text=f"{airport_name}'s K-Factor from {startdate} to {enddate} | {inout_p2}",title_x=0.5)
    # fig.update_layout(legend = dict(font = dict(family = "Open Sans, monospace", size = 16, color = "black")),
    #               legend_title = dict(font = dict(family = "Open Sans, monospace", size = 16, color = "black")))
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

    fig1.update_layout(showlegend=True, title_text=f"{airport_name}'s Results from {startdate} to {label_date[1]} | {inout_p2}",title_x=0.5, barmode='stack',
    xaxis_title="Time",yaxis_title="Passenger",
    font=dict(size=14,color="Black",family='Open Sans, monospace'),
    legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
 
    fig1.update_xaxes(type="date", range=[startdate,label_date[2]], rangemode='normal',title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    fig1.update_yaxes(title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'),range=[-20, df_chart.Passenger.max()+200])

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    print('passenger max is',df_chart.Passenger.max())
    return render_template("plotly_part2.html",
    k_factor = k_factor,
    label_date = label_date, 
    graphJSON = graphJSON, 
    graphJSON1 = graphJSON1,
    inout_p2 = inout_p2,
    airport_data2 = airport_data2)
    #return test_df.to_html()

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    #return update_graph(request.args.get('data'))
    #if request.method == 'POST':
        #test = request.form['test']
    start_date = request.args.get('data') #This is a str type
        #end_date = request.form['end_date'] #This is a str type
    end_date = request.args.get('data1')
    inout_p2 = request.args.get('data2')
    airport_data2 = request.args.get('data3')
    print('StartDate',start_date)
    print('Enddate is',end_date)
    print('==================',inout_p2)
    print('*****************************', airport_data2)
    #print('===============',type(test), start_date,end_date)
    return update_graph(start_date,end_date,inout_p2,airport_data2)
    
def update_graph(startdate,enddate,inout_p2,airport_data2):

    if inout_p2 == 'Arrival':
        data_test = data_in
    else:
        data_test = data_out

    airport_name = capacity_insert.format_airport(airport_data2)

    data_test = data_test[data_test.AirportNameTH == airport_data2]
    df_test = makedatetime.convertdate(data_test)
    df_test['date'] = [date.strftime("%Y-%m-%d") for date in df_test.index.date]
    df_test = df_test.sort_index()
    test_df = makedatetime.select_time(df_test,startdate,enddate)
    test_df = test_df.dropna()
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


    fig1.update_layout(showlegend=True, title_text=f"{airport_name}'s Results from {startdate} to {enddate} | {inout_p2}",title_x=0.5, barmode='stack',
    xaxis_title="Time",yaxis_title="Passenger",
    font=dict(size=14,color="Black",family='Open Sans, monospace'),
    legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))

    fig1.update_xaxes(type="date", rangemode='normal', range=[startdate,label_date[np.where(label_date == enddate)[0][0]+1]],title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    fig1.update_yaxes(title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    graphJSON2 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON2

#============================================================================ Part3 =========================================================================
@app.route('/predictpassenger', methods=["GET","POST"])
def predict():
    # data = randomforestdata
    # return data.to_html()
    return render_template("part3.html",airport = airport)

@app.route('/displaypart3', methods=["GET", "POST"])
def modelpredict():
    if request.method == 'POST':
        startdate = request.form['startdate'] #This is a str type
        enddate = request.form['enddate'] #This is a str type
        inout_p3 = request.form['inout']
        airport_data3 = request.form['airport_data']
  
    if inout_p3 == 'Arrival':
        data = data_in
    else:
        data = data_out

    #data = data_in
    airport_name = capacity_insert.format_airport(airport_data3)
    data = data[data.AirportNameTH == airport_data3]
    test = prediction.converttime(data)
    test = test[test.PASSENGER != 0]

    df = prediction.resam(test)
    df = prediction.getdatevalue(df) #train data
    #df = prediction.getoldpassenger(df)
    #df = prediction.select_time(df,'2015-01-01','2019-12-31')

    #df = prediction.merge(df,factor,factor_date)
    gen = ['Year','Month','Week','Date','Hour','Dayofweek','Previous','2Previous','3Previous','4Previous']
    
    enddate1 = prediction.plusdate(enddate)
    daterange = pd.date_range(start=startdate, end=enddate1, freq='3H')
    # df_datetime = daterange.to_frame(name = 'DateTime')
    df_datetime = daterange.to_frame(name = 'date_and_time')
    df_datetime = df_datetime[:-1]

    df_time = prediction.getdatevalue(df_datetime) #predict data

    input_data = pd.concat([df, df_time], ignore_index=True)
    input_data = prediction.getoldpassenger(input_data,df,df_time)

    #df_train = prediction.select_time(input_data,'2015-01-01','2019-12-31')
    df_train = input_data[8766:8766+14608]
    #df_train = df_train[df_train.PASSENGER != 0]
    df_train = df_train.fillna(0)

    df_predict = input_data.set_index('date_and_time')
    df_predict = df_predict[23374:]
    df_predict = df_predict.drop('PASSENGER',axis=1)
    df_predict = df_predict.fillna(0)

    predict = prediction.randomforest(df_train,df_predict,gen)
    predict = predict.reset_index()
    predict['datecol'] = [date.strftime("%Y-%m-%d") for date in predict.date_and_time]
    predict['datetimecol'] = [date.strftime("%Y-%m-%d %H:%M:%S") for date in predict.date_and_time]
    label_date = predict.datecol.unique()

    predictvalue = list(predict.Predict)
    predictdate = list(predict.datetimecol)

    fig = px.line(data_frame = predict, 
    x = 'date_and_time', 
    y = 'Predict',color_discrete_sequence=['orange']
    )

    fig.update_layout(
    showlegend=True, modebar_remove=True,hovermode='closest',
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    font=dict(size=14,color="Black",family='Open Sans, monospace'),
    hoverlabel=dict(bgcolor="white",font_size=16),
    title_text=f"{airport_name} Passengers Prediction from {startdate} to {enddate} | {inout_p3}",title_x=0.5)
    fig.update_xaxes(title = 'Date',title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    fig.update_yaxes(title = 'Passenger',title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #predict_json = predict.to_json(orient="split")
    return render_template("plotly_part3.html",graphJSON = graphJSON, label_date=label_date, inout_p3 = inout_p3, predictvalue=predictvalue, predictdate=predictdate,airport_data3 = airport_data3)
    #return df_train.to_html()

@app.route('/callback1', methods=['POST', 'GET'])
def cb3():

    start_date = request.args.get('data') #This is a str type
    end_date = request.args.get('data1')
    inout_p3 = request.args.get('data2')
    data_date = request.args.getlist('data3[]')
    data_predict = request.args.getlist('data4[]')
    airport_data3 = request.args.get('data5')
    
    #data = request.args.get('data3')
    # print('StartDate',start_date)
    # print('Enddate is',end_date)
    # print('==================',inout_p3)


    #print('********************', list(data_list))

    #print('===============',type(test), start_date,end_date)
    return update_graph3(start_date,end_date,inout_p3,data_date,data_predict,airport_data3)
    
def update_graph3(startdate,enddate,inout_p3,data_date,data_predict,airport_data3):
    
    
    # if inout_p3 == 'Arrival':
    #     data_test = data_in
    # else:
    #     data_test = data_out
    airport_name = capacity_insert.format_airport(airport_data3)
    # data = data_test
    zipped = list(zip(data_date,data_predict))
    pre = pd.DataFrame(zipped, columns=['DateTime', 'Passenger'])
    pre['Date'] = pd.to_datetime(pre['DateTime']).dt.date
    pre['Date'] = pre['Date'].astype(str)
    pre['Passenger'] = pre['Passenger'].astype(int)
    list_date = list(pre.Date.unique())


    fig1 = px.line(pre, x="DateTime", y="Passenger",color_discrete_sequence=['orange'])
    
    # fig.update_layout(
    # showlegend=True, modebar_remove=True,hovermode='closest',
    # legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    # font=dict(size=14,color="Black",family='Open Sans, monospace'),
    # hoverlabel=dict(bgcolor="white",font_size=16))
    fig1.update_layout(
    showlegend=True, modebar_remove=True,hovermode='closest',
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    font=dict(size=14,color="Black",family='Open Sans, monospace'),
    hoverlabel=dict(bgcolor="white",font_size=16),
    title_text=f"{airport_name} Passengers Prediction from {startdate} to {enddate} | {inout_p3}",title_x=0.5)
    fig1.update_xaxes(type ='date', range=[startdate,list_date[list_date.index(enddate)+1]],title = 'Date',title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    fig1.update_yaxes(title = 'Passenger',title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    # data = data[data.AirportNameTH == 'ท่าอากาศยานกระบี่']
    # test = prediction.converttime(data)
    # test = test[test.PASSENGER != 0]
    # df = prediction.resam(test)
    # df = prediction.getdatevalue(df)
    # #df = prediction.getoldpassenger(df)
    # #df = prediction.select_time(df,'2015-01-01','2019-12-31')

    # #df = prediction.merge(df,factor,factor_date)
    # gen = ['Year','Month','Week','Date','Hour','Dayofweek','Previous','2Previous','3Previous']
    
    # daterange = pd.date_range(start=startdate, end=enddate, freq='6H')

    # df_datetime = daterange.to_frame(name = 'date_and_time')
    # df_time = prediction.getdatevalue(df_datetime)

    # input_data = pd.concat([df, df_time], ignore_index=True)
    # input_data = prediction.getoldpassenger(input_data,df,df_time)

    # df_train = prediction.select_time(input_data,'2015-01-01','2019-12-31')
    # df_train = df_train[df_train.PASSENGER != 0]
    # df_train = df_train.dropna()

    # df_predict = input_data.set_index('date_and_time')
    # df_predict = df_predict.loc[startdate:enddate]
    # df_predict = df_predict.drop('PASSENGER',axis=1)
    # df_predict = df_predict.dropna()
    # df_predict = df_predict[df_predict.Previous != 0]

    # predict = prediction.randomforest(df_train,df_predict,gen)
    # predict = predict.reset_index()
    # predict['datecol'] = [date.strftime("%Y-%m-%d") for date in predict.date_and_time]
    # label_date = predict.datecol.unique()
    # fig = px.line(data_frame = predict, 
    # x = 'date_and_time', 
    # y = 'Predict',
    # title = 'Passengers Prediction from {startdate} to {enddate} |')

    # fig.update_layout(
    # showlegend=True, modebar_remove=True,hovermode='closest',
    # legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    # font=dict(size=14,color="Black",family='Open Sans, monospace'),
    # hoverlabel=dict(bgcolor="white",font_size=16),
    # title_text=f"Passengers Prediction from {startdate} to {enddate} |",title_x=0.5)
    # fig.update_xaxes(type ='date', range=[startdate,label_date[np.where(label_date == enddate)[0][0]]],title = 'Date',title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    # fig.update_yaxes(title = 'Passenger',title_font=dict(size=18,color="Black"),tickfont=dict(size=16,color='Black',family='Open Sans, monospace'))
    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON1
    #return true_data.to_html()
    #return "hello"

if __name__ == "__main__":
    app.run(port=80,debug=True)