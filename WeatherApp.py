# WeatherApp.py
# by James Ye

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
		f"<center>"
        f"Available Routes:<br/>"
		f"<br/>"		
        f"<a href = '/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
		f"<br/>"
        f"<a href = '/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
		f"<br/>"
		f"<a href = '/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
		f"<br/>"
		f"/api/v1.0/start<br/>"
		f"(example: <a href = '/api/v1.0/2016-08-25'>/api/v1.0/2016-08-25</a>)<br/>"
		f"<br/>"
		f"/api/v1.0/start/end<br/>"
		f"(example: <a href = '/api/v1.0/2016-08-25/2017-01-09'>/api/v1.0/2016-08-25/2017-01-09</a>)<br/>"
		f"</center>"
    )
	

@app.route("/api/v1.0/precipitation")
def precipitation():
	# Create our session (link) from Python to the DB
	session = Session(engine)
	
	# results is a list of tuples, the tuples are in the form of (date, prcp)
	results = session.query(Measurement.date, Measurement.prcp).all()
	session.close()
	
	all_precipitations = []
	for date, prcp in results:
		prcp_dict = {}
		prcp_dict[date] = prcp
		all_precipitations.append(prcp_dict)
	
	return jsonify(all_precipitations)


@app.route("/api/v1.0/stations")
def stations():	
	session = Session(engine)
	
	# results is a list of Station objects, since I did not specified column names
	results = session.query(Station)
	session.close()
	
	all_stations = []

	# loop through each station object
	for row in results:
		station_dict = {}
		station_dict['elevation'] = row.elevation
		station_dict['latitude'] = row.latitude
		station_dict['station'] = row.station
		station_dict['longitude'] = row.longitude
		station_dict['name'] = row.name
		station_dict['id'] = row.id
		all_stations.append(station_dict)

	return jsonify(all_stations)
		

@app.route("/api/v1.0/tobs")
def tobs():
	session = Session(engine)
	st_count = func.count(Measurement.station)
	most_active_station = session.query(Measurement.station, st_count).group_by(Measurement.station).order_by(st_count.desc()).first()[0]
	
	print(f"most_active_station: {most_active_station}")
	
	
	# Calculate the date 1 year ago from the last data point in the database
	last_date = session.query(func.max(Measurement.date)).filter_by(station = most_active_station).scalar()
	print(f"last_date: {last_date}")
	
	last_date_minus_12m = (dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)).date()
	print(f"last_date_minus_12m: {last_date_minus_12m}")
	
	last_12month_tobs = session.query(Measurement.date, Measurement.tobs).filter_by(station = most_active_station).filter(Measurement.date > last_date_minus_12m).all()
	
	session.close()
	
	all_tobs = []
	for date, tobs in last_12month_tobs:
		tobs_dict = {}
		tobs_dict[date] = tobs
		all_tobs.append(tobs_dict)
	
	return jsonify(all_tobs)	
	

@app.route("/api/v1.0/<start>")
def get_temp1(start):
	start_date = start
	end_date = dt.date.today()
	
	results = calc_temps(start_date, end_date)
	
	return jsonify(results)


@app.route("/api/v1.0/<start>/<end>")
def get_temp2(start, end):
	start_date = start
	end_date = end
	
	results = calc_temps(start_date, end_date)
	
	return jsonify(results)	


def calc_temps(start_date, end_date):
	"""TMIN, TAVG, and TMAX for a list of dates.

	Args:
		start_date (string): A date string in the format %Y-%m-%d
		end_date (string): A date string in the format %Y-%m-%d
		
	Returns:
		TMIN, TAVE, and TMAX
	"""
	session = Session(engine)
	results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
				func.max(Measurement.tobs)).\
				filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
	session.close()
	
	return results

	
# this part must be placed at the end of the file!!	
if __name__ == '__main__':
    app.run(debug=True)


	

	
	

