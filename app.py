# Import dependencies
from types import prepare_class
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

###########################################

# Setting up data base
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Find the most recent date in the data set.
session = Session(engine)
recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

# Calculate the date one year from the last date in data set.
one_year_from_date = dt.date(2017,8,23) - dt.timedelta(days=365)

session.close()

############################################
# Flask Set up
############################################
app = Flask(__name__)

############################################
# Flask routes
############################################

# Home page that lists all routes that are available
@app.route("/")
def home():
     """List all available API routes."""
     
     return (
        f"Welcome to my Hawaii Climate SQL-Alchemy App API!<br/>"
        f"Available Routes:<br/>"

        f"A list of Precipitation data with dates:<br/>"
        f"      /api/v1.0/precipitation<br/>"

        f"A list of all stations and their names:<br/>"
        f"      /api/v1.0/stations<br/>"

        f"A list of Temperature Observations (TOBS) over the past year from the most recent date:<br/>"
        f"      /api/v1.0/tobs<br/>"

        f"A list of min, max. and average temperatures for the given start date (use 'yyyy-mm-dd' format):<br/>"
        f"      /api/v1.0/[start_date format:yyyy-mm-dd]<br/>"

        f"A list of min, max. and average temperatures for the given date range (use 'yyyy-mm-dd'/'yyyy-mm-dd' format):<br/>"
        f"      /api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
     )

#############################################

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Session link
    session = Session(engine)

    """Return a list of Precipitation data"""
    # Query
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date>=one_year_from_date).all()

    session.close()

    # Create dictionary
    precipitation = []
    for result in results:
        precip = {}
        precip[result[0]] = result[1]

        precipitation.append(precip)

    return jsonify(precipitation)

##############################################

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Session link
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Query
    results = session.query(station.station, station.name).all()

    session.close()

    # Create station list
    station_list = []
    for result in results:
        station_data = {}
        station_data["station"] = result[0]
        station_data["name"] = result[1]

        station_list.append(station_data)

    return jsonify(station_list)

##############################################

# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Session link
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS) for the previous year of the most active station"""
    # Query
    results = session.query(measurement.date,  measurement.tobs,measurement.prcp).filter(measurement.date >= one_year_from_date).filter(measurement.station=='USC00519281').order_by(measurement.date).all()

    session.close()

    # Create tobs list
    tobs_list = []
    for date, prcp, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["prcp"] = prcp
        tobs_dict["tobs"] = tobs
        
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

##############################################  

# Start date route
@app.route("/api/v1.0/<start_date>")
def Start_date(start_date):
    # Session link
    session = Session(engine)

    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    # Query
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date>= start_date).all()

    session.close()

    # Create start date list
    start_date_list = []
    for min, avg, max in results:
        start_date_dict = {}
        start_date_dict["min_temp"] = min
        start_date_dict["max_temp"] = max
        start_date_dict["avg_temp"] = avg

        start_date_list.append(start_date_dict) 

    return jsonify(start_date_list)

##############################################  

# Start and end date route
@app.route("/api/v1.0/<start_date>/<end_date>")
def Start_and_end_date(start_date, end_date):
    # Session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    # Query
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date>= start_date).filter(measurement.date<= end_date).all()

    session.close()

    # Create start and end date list
    start_end_date_list = []
    for min, avg, max in results:
        start_end_date_dict = {}
        start_end_date_dict["min_temp"] = min
        start_end_date_dict["max_temp"] = max
        start_end_date_dict["avg_temp"] = avg

        start_end_date_list.append(start_end_date_dict) 

    return jsonify(start_end_date_list)

##############################################  

# Run the app
if __name__ == "__main__":
    app.run(debug=True)