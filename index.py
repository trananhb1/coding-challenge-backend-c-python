from flask import Flask, request, jsonify
import pandas as pd
from math import sin, cos, sqrt, atan2, radians

app = Flask(__name__)

@app.route('/')
def index():
    return 'use /suggestions'


@app.route('/suggestions', methods=['GET'])
def suggestions():
    # Get user input from parameter
    print (request.args)
    if len(request.args) > 0:
        params = request.args.to_dict()
        if params['q'] != '':
            city = params['q']
            lat = float(params['latitude']) if 'latitude' in params.keys() else 0
            lon = float(params['longitude']) if 'longitude' in params.keys() else 0
            
            # Load processed city and return to json 
            list_city = load_city(city,lat,lon)
            result={'suggestion':list_city.to_dict('record')}
            print(result)            
        else:
            result = 'There is no city input'
    else:
        result = 'Put some parameters'
    return result, 200
    


def load_city(city,lat,lon):
    # Load dataset of city from file: 
    cities_load = pd.read_csv('cities_canada-usa.tsv', sep='\t')

    # Select certain columns
    columns = ['name','country','admin1','lat','long']

    # Filter the city based on user input to minimize the score calculation
    cities_match = cities_load[cities_load['name'].str.contains(city)][columns]
    
    # check if user input longtitude and latitude
    if lat != 0 and lon != 0:
        # convert columns lat & long to float64
        type_colums = ['lat', 'long']
        cities_match[type_colums] = cities_match[type_colums].astype(float)

        # Calculate distance between 2 coordinations
        cities_match['distance']=cities_match.apply(lambda d: distance(d["long"],d['lat'],  lon, lat ), axis=1)

        # Calculate score based on coordinations
        cities_match['score']=cities_match.apply(lambda d: calculatescore(d["long"],d['lat'],  lon, lat ), axis=1)         
        cities_match['score2']=cities_match.apply(lambda d: newcalculatescore(d["long"],d['lat'],  lon, lat ), axis=1)

        # Customize and reformat data generated 
        cities_match.sort_values(by='score2', ascending=False, inplace=True)         
        cities_match['name']=cities_match.apply(lambda d: ''+d['name']+', '+d['admin1']+', '+d['country'] , axis=1)
        cities_match.drop(['country', 'admin1'], inplace=True,axis=1)
        cities_match.rename(columns={'lat':'latitude', 'long':'longtitude'}, inplace=True)
        cities_match.reset_index(drop=True, inplace=True)
            
    return cities_match


# Calculate distance between 2 coordinations
def distance(lon1, lat1, lon2, lat2):
    R = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# Scoring the city suggestions 

def calculatescore(lon1, lat1, lon2, lat2):
    lat = abs(lat2 - lat1)
    lon = abs(lon2 - lon1)
    score = 10 - (lat + lon) / 2
    score = round(score,0) / 10 if score > 0 else 0
    return score

def newcalculatescore(lon1, lat1, lon2, lat2):
    distanceKm = distance(lon1, lat1, lon2, lat2)
    score = 1000 - distanceKm
    score = round(score/10,0) / 100 if score > 0 else 0
    return score