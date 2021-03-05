"""This script stores dataframe to sql database"""

from sql_db import Database
import argparse

def main(filepath, db_name, db_config, section):
    """Stores data to the sql server"""

    db = Database(db_config, section)
    db.connect()
    db.overwrite_df_on_sql(filepath, db_name)

if __name__ == "__main__":
    # setup argparser
    parser = argparse.ArgumentParser(description='Code stores dataframe to sql server...')
    parser.add_argument('--inp', type=str,
                        help='Path to the pickle file storing the dataframe.')
    parser.add_argument('--db', type=str, help='Database name')
    parser.add_argument('--cfg', type=str, default="Database.ini",
                        help='Database config file path. Default is "Database.ini"')
    parser.add_argument('--sect', type=str, default="postgresql",
                        help='Database config section name to use. Default is "postgresql"')
    args = parser.parse_args()

    # call main function
    main(args.inp, args.db, args.cfg, args.sect)