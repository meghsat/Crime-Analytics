import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import datetime
import pandas as pd
from flask import make_response
import pandas as pd
import numpy as np
import os # Operating System
import numpy as np
import pandas as pd
import datetime as dt # Datetime
import json # library to handle JSON files
from waitress import serve
#!conda install -c conda-forge geopy --yes
# from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

#!conda install -c conda-forge folium=0.5.0 --yes
import folium #import folium # map rendering library
app = Flask(__name__)
model = pickle.load(open('models/blocknaive36', 'rb'))
#modeltime=pickle.load(open('models/finalized_modelmain', 'rb'))

# @app.route('/predict2',methods=['POST'])
# def predict2():
#     int_features = [int(x) for x in request.form.values()]
#     final_features = np.array([np.array(int_features)])
#     # if(final_features.shape[0]!=0&final_features.shape[1]!=0):
#     prediction = modeltime.predict(final_features)
#     output = prediction

#     return render_template('time.html', prediction_text='Crime Predicted {}'.format(output))
#     # else:
#     #     return render_template('time.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/time')
def time():
    return render_template('time.html')

@app.route('/index2')
def index2():
    return render_template('index2.html')
@app.route('/predict3',methods=['POST'])
def predict3():
    int_features = [int(x) for x in request.form.values()]
    final_features = np.array([np.array(int_features)])
    # if(final_features.shape[0]!=0&final_features.shape[1]!=0):
    prediction = model.predict(final_features)
    output = prediction

    return render_template('index.html', prediction_text='Crime Predicted {}'.format(output))
    # else:
    #     return render_template('time.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    location=request.form.get("Location");
    startdate=request.form.get("startdate");
    enddate=request.form.get("enddate");
    
    startdate1=datetime.datetime.strptime(startdate,"%Y-%m-%d")
    startmonth=startdate1.month
    startday=startdate1.day

    enddate1=datetime.datetime.strptime(enddate,"%Y-%m-%d")
    endmonth=enddate1.month
    endday=enddate1.day
    df=pd.DataFrame(columns=['TimeStamp','Location','Crime','Latitude','Longitude'])
    initial=0
    geolocator=Nominatim(user_agent="bglr_explorer")
    for i in range(startmonth,endmonth+1):
        if initial==0:
            for j in range(startday,endday+1):
                for hour in range(1,24):
                    for minute in range(1,60):
                        features=[location,i,j,hour,minute]
                        features=[np.array(features)]
                        prediction=model.predict(features)
                        date=str(startdate1.year)+"-"+str(i)+"-"+str(j)+" "+str(hour)+":"+str(minute)
                        b=geolocator.geocode(location,timeout=10000)
                        
                        latitude=b.latitude
                        longitude=b.longitude
                        df=df.append({'TimeStamp':date,'Location':location,'Crime':prediction,'Latitude':latitude,'Longitude':longitude},ignore_index=True)
                        initial=1
       
        else:
            for j in range(1,31):
                for hour in range(1,24):
                    for minute in range(1,60):
                        features=[location,i,j,hour,minute]
                        features=[np.array(features)]
                        #features=features.reshape(1,-1)
                        prediction=model.predict(features)
                        date=str(startdate1.year)+"-"+str(i)+"-"+str(j)+" "+str(hour)+":"+str(minute)
                        a=location
                        b=geolocator.geocode(a,timeout=10000)
                        latitude=b.latitude
                        longitude=b.longitude
                        df=df.append({'TimeStamp':date,'Location':location,'Crime':prediction,'Latitude':latitude,'Longitude':longitude},ignore_index=True)
    df.to_csv("crimedata.csv")
    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    
    return resp
    #return render_template('index2.html', prediction_text='Crime Predicted {}'.format(df))

@app.route('/maps')
def maps():
    df=pd.read_csv("mapp.csv")
    from geopy.geocoders import Nominatim
    address = 'Vijayawada, In'

    geolocator = Nominatim(user_agent="bg_explorer")
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude
    map_bnglr = folium.Map(location=[latitude, longitude], zoom_start=10)
    blocks=[]
    colors_array = cm.rainbow(np.linspace(0, 1, 3100))
    rainbow=[colors.rgb2hex(i) for i in colors_array]
    i=1
    for index, row in df.iterrows():
        block=row['Block']
        lat=row['Latitude']
        lng=row['Longitude']
        label='{}'.format(block)
        #a=df.loc[df.Block == str(poi), 'Block'].count()
        label = folium.Popup(label+'Crimes Happened='+str(0), parse_html=True)
        if block not in blocks:      
        #print(block)
            blocks.append(block)
            folium.CircleMarker(
            [lat, lng],
            radius=5,
            popup=label,
            color=rainbow[int(i)-1],
            fill=True,
            fill_color='#3186cc',
            fill_opacity=0.7,
            parse_html=False).add_to(map_bnglr)
            i=i+1
    map_bnglr.save('templates/map.html')
    return render_template('index2.html',folium_map=map_bnglr)
@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/about')
def about():
    return render_template('about2.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/predict_api',methods=['POST'])
def predict_api():
    '''
    For direct API calls trought request
    '''
    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)

if __name__ == "__main__":
    app.run()