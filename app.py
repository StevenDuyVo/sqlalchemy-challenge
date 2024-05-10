# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with = engine)

# Save references to each table
station = base.classes.station
measurement = base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App!<br/>"
        f"<br/>Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt; - Input date as yyyy-mm-dd<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; - Input date as yyyy-mm-dd"
    )

# /api/v1.0/precipitation" route
@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    twelve_months_ago = most_recent_date - dt.timedelta(days=366)
    
    precipitation_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= twelve_months_ago).all()
    
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

# /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(station.station).all()
    
    station_list = [station for station, in stations]
    
    return jsonify(station_list)

# /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station_id = session.query(measurement.station).group_by(measurement.station).order_by(func.count().desc()).first()[0]
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    most_recent_date = most_recent_date[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    twelve_months_ago = most_recent_date - dt.timedelta(days=366)

    temperature_data = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station_id).filter(measurement.date >= twelve_months_ago).all()
    
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]
    
    return jsonify(temperature_list)

# /api/v1.0/<start> route
@app.route("/api/v1.0/<start>")
def temp_start(start):
    temperatures = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    
    temp_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temperatures]
    
    return jsonify(temp_list)

# /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    # Query TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    temperatures = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    # Convert the query results to a list of dictionaries
    temp_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temperatures]
    
    return jsonify(temp_list)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)