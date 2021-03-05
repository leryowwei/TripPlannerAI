import psycopg2
import os
import io
import pandas
from sqlalchemy.engine.url import URL
from configparser import ConfigParser
from pandas import DataFrame
from sqlalchemy import create_engine

def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(os.path.join(os.path.abspath(""), filename))

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return URL(**db)

def connect():
    """ Connect to the PostgreSQL database server """
    engine = None
    try:
        # read connection parameters
        db_uri = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        engine = create_engine(db_uri)

        # create connection
        conn = engine.connect()

        # execute a statement to get version of postgres
        print('PostgreSQL database version:')
        db_version = conn.execute('SELECT version()')
        print(db_version.fetchone()[0])

        # close the communication
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return engine


filepath = "D:/Documents/GitHub/TripPlannerAI/Data_wrangler/TripPlannerData_20210305_221511.pkl"

df = pandas.read_pickle(filepath)
#df.iloc[:, df.columns.get_loc('hardcoded_durations')] = 0
#df.iloc[:, df.columns.get_loc('styles_score_nlp')] = 0
#df.iloc[:, df.columns.get_loc('wordfinder_scores')] = 0

temp_df = df

print(temp_df[0:])

# create database engine
engine = connect()

# create dataframe
temp_df.to_sql('df_04032021', engine, if_exists='replace')
