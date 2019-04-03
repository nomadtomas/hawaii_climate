# Use in combination with db_base.py for boilerplate SQLalchemy 
from flask import Flask, json, jsonify
import datetime as dt
import numpy as np
from db_base import engine, func, session, Measurement, Station

app = Flask(__name__)

@app.route('/')
def home_route():
    """ Available API Route Endpoints"""
    return (f"Enter Available Route Endpoints.  Where dates are required, modify date selection as desired: <br><br/>"
        f"1.   Dates & temps dictionary:   <br/>"
        f"   /api/v1.0/precipitation/ <br><br/>" 
        f"2.   JSON list of stations:    <br/>"
        f" /api/v1.0/stations/ <br><br/>" 
        f"3.    JSON list of Temp Observations:  <br/>"
        f" /api/v1.0/tobs/ <br><br/>"
        f"Please enter date as form 'yyyy' or 'yyyy-mm' or 'yyyy-mm-dd' <br><br/>"
        f"4.    Stats Combined Stations. Enter Start date:  <br/>"
        f" /api/v1.0/2017-01-01 <br><br/>" 
        f"5.    Stats Combined Stations. Enter Start & End Date:  <br/>"
        f" /api/v1.0/2017-01-01/2018-08-29 <br><br/><end>")
        
#    Convert the query results to a Dictionary using 'date' as the key and 'tobs' as the value.
#    Return the JSON representation of your dictionary
@app.route('/api/v1.0/precipitation/')
def precipitation():
    # 365 days from most_recent
    prev_yr_date = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    
    # Date and prcp values
    prcp_results = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.date >= prev_yr_date).all()
    p_dict = dict(prcp_results)
    print()
    print("Results for Precipitation")
    return jsonify(p_dict) 

#    Return a JSON-list of stations from the dataset.
@app.route('/api/v1.0/stations/')
def stations():
    station_list = session.query(Station.station)\
    .order_by(Station.station).all() 
    print()
    print("Station List:") 
    list_stations = list(station_list)  
    return jsonify(list_stations)

#    Query for the dates and temperature observations from a year from the last data point.
#    Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route('/api/v1.0/tobs/')
def tobs():
    prev_yr_date = dt.datetime(2017,8,23) - dt.timedelta(days=365)

    temp_obs = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.date >= prev_yr_date)\
    .order_by(Measurement.date).all()
    print()
    print("Temperature Results for All Stations")
    return jsonify(temp_obs)

# Return a JSON-list of Temperature Observations from the previous year.
#   /api/v1.0/<start  and /api/v1.0/<start>/<end>
#find the temp min, max, and avg for a date range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def agg_start_list(start=None,end=None):
    #Data for tmin,tavg,tmax vals
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    def get_date(date1):
        year, month, day = map(int, date1.split('-'))
        converted_to_date= dt.datetime(year, month, day)
        return converted_to_date
    # check if start date and end end are provided or not
    if start is not None and end is not None:
        start_date=get_date(start)
        end_date =get_date(end)
        agg_list=session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    elif start is not None and end is None:
        start_date=get_date(start)
        agg_list=session.query(*sel).filter(Measurement.date >= start_date).all()
    new_agg=np.ravel(agg_list)   
    return jsonify({"min":new_agg[0],"avg":new_agg[1],"max":new_agg[2]})

app.run(debug=True)