import psycopg2
import os
import pandas as pd
from sqlalchemy.engine.url import URL
from configparser import ConfigParser
from sqlalchemy import create_engine

class Database:
    """Class to access postgress sql database"""
    def __init__(self, filename = 'database.ini', section ='postgresql'):
        self.config_filename = filename
        self.config_section = section
        self.engine = None

    def config(self):
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(os.path.join(os.path.abspath(""), self.config_filename))

        # get section, default to postgresql
        db = {}
        if parser.has_section(self.config_section):
            params = parser.items(self.config_section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(self.config_section, self.config_filename))

        return URL(**db)

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            # read connection parameters
            db_uri = self.config()

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.engine = create_engine(db_uri)

            # create connection
            conn = self.engine.connect()

            # execute a statement to get version of postgres
            print('PostgreSQL database version:')
            db_version = conn.execute('SELECT version()')
            print(db_version.fetchone()[0])

            # close the communication
            conn.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def get_engine(self):
        return self.engine

    def overwrite_df_on_sql(self, filepath, db_name):
        """Reads from pkl file and overwrites the data on sql database"""
        df = pd.read_pickle(filepath)
        df.to_sql(db_name, self.engine, if_exists="replace")
        print("Database for {} successfully created on sql server...".format(db_name))

    def read_df_from_sql(self, db_name):
        """Saves the whole dataframe from sql"""
        return pd.read_sql_table(db_name, self.engine)