import os
import sys
import result_parser
import pymysql
import mysql_helper
import settings
import csv_processor
from secure_settings import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_USER

def main():

    if (len(sys.argv) < 2):
        script_name = os.path.basename(__file__)
        print ("Usage: " + script_name + " <filename>")
    else:
        filename = sys.argv[1]
        with open(filename, "r") as input_file:
            input_data = input_file.read()
         
        mapped_results = result_parser.parse_results(input_data)
         
        save_to_tsv_file(os.path.splitext(filename)[0] + ".tsv", mapped_results)
        save_to_db(mapped_results)
        print("Finished.")

def save_to_db(mapped_results):
    db_connection = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, database=DB_DATABASE)
    
    mysql_helper.drop_table(db_connection, settings.TABLE_DEFS["result"]["name"])
    mysql_helper.create_table(db_connection, settings.TABLE_DEFS["result"])
    mysql_helper.insert_rows(db_connection, settings.TABLE_DEFS["result"], mapped_results)
    db_connection.close()

def save_to_tsv_file(filename, mapped_results):
    output_data = csv_processor.rows_to_csv(mapped_results, "\t")
    base_filename = os.path.splitext(filename)[0]
    with open(base_filename + ".tsv", "w") as output_file:
        output_file.write(output_data)

if __name__ == "__main__":
    main()
