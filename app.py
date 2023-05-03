# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)
def prev_year():
    session = Session(engine)
    most_recent = session.query(func.max(Measurement.date)).first()[0]
    initial_date = dt.datetime.strptime(most_recent, "%Y-%m-%d") - dt.timedelta(days=365)

                      
    session.close()
    return(initial_date)


#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return """ <h1> Honolulu Climate API </h1>
    <ul>
    <li>Precipitation: <strong>/api/v1.0/precipitation</strong> </li>
    <li> Stations: <strong>/api/v1.0/stations</strong></li>
    <li>TOBS: <strong>/api/v1.0/tobs</strong></li>
    <li>Temperatures for a specific start date: <strong>/api/v1.0/&ltstart&gt</strong> (start date: yyyy-mm-dd)</li>
    <li>Temperatures for a specific start-end range: <strong>/api/v1.0/&ltstart&gt/&ltend&gt</strong> (start/end date: yyyy-mm-dd)</li>
    </ul>
    """

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prep_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year()).all()
                  
    session.close()
    prep_list = []
    for date, prep in prep_data:
        prep_dict = {}
        prep_dict["date"] = date
        prep_dict["prep"] = prep
        prep_list.append(prep_dict)

    return jsonify(prep_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stat_data = session.query(Station.station).all()

    session.close()

    stat_list = list(np.ravel(stat_data))

    return jsonify(stat_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= prev_year()).all()

    session.close()

    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def cal_temp(start=None, end=None):
    session = Session(engine)
    
    if end == None: 
        start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()
        start_list = list(np.ravel(start_data))

        return jsonify(start_list)
    else:
        date_range_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
        date_range_list = list(np.ravel(date_range_data))

        return jsonify(date_range_list)

    session.close()
    
if __name__ == "__main__":
    app.run(debug = True)