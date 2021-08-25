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
        f"Welcome to my SQL-Alchemy App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
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

@app.route("/api/v1.0/tobs")
def tobs():
    # Session link
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS) for the previous year"""
    # Query
    results = session.query(measurement.tobs, measurement.date).filter(measurement.date>=one_year_from_date).all()

    session.close()

    # Create tobs list
    tobs_list = []
    for result in results:
        tobs_data = {}
        tobs_data["temperature"] = result[0]
        tobs_data["date"] = result[1]
        tobs_list.append(tobs_data)

    return jsonify(tobs_list) 

##############################################  



# Run the app
if __name__ == "__main__":
    app.run(debug=True)