import os
import sys
from parsers import result_parser
from parsers import race_parser
import pymysql
import settings
from helpers import mysql_helper, csv_helper
from secure_settings import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_USER

def main():
    if (len(sys.argv) < 2):
        script_name = os.path.basename(__file__)
        print ("Usage: " + script_name + " <directory>")
    else:
        path = sys.argv[1]
        filenames = [os.path.join(path,fn) for fn in os.listdir(path)] 
         
        parse_output = parse_files(filenames)
        results = parse_output["results"]
        race_info = parse_output["race_info"]
        
        save_to_tsv_file("all_results.tsv", results)
        save_to_db(results, settings.TABLE_DEFS["result"])
        save_to_db(race_info, settings.TABLE_DEFS["race"])
        print("Finished.")

def save_to_db(dataset, table_def):
    db_connection = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, database=DB_DATABASE)
    
    mysql_helper.drop_table(db_connection, table_def["name"])
    mysql_helper.create_table(db_connection, table_def)
    mysql_helper.insert_rows(db_connection, table_def, dataset)
    
    db_connection.close()

def save_to_tsv_file(filename, mapped_results):
    output_data = csv_helper.rows_to_csv(mapped_results, "\t")
    base_filename = os.path.splitext(filename)[0]
    with open(base_filename + ".tsv", "w") as output_file:
        output_file.write(output_data)

def parse_files(filename_list):
    race_id = 1
    multiple_file_parse = {"race_info": [], "results": []}

    for filename in filename_list:
        if not filename.endswith(".txt"):
            continue

        file_parse = parse_file(filename, race_id)
        if file_parse:
            multiple_file_parse["race_info"].append(file_parse["race_info"])
            multiple_file_parse["results"].extend(file_parse["results"])
        race_id += 1

    return multiple_file_parse

def parse_file(filename, race_id):
    with open(filename, "r") as input_file:
        data_from_file = input_file.read()

    header_lines = result_parser.get_header(data_from_file)
    if not header_lines:
        print("%s: Could not read header" % filename)
        return
    
    results = result_parser.get_results(filename, header_lines, data_from_file)
    if not results: 
        return

    add_to_each_row(results, {"race_id":race_id})

    race_info = race_parser.get_race_info(result_parser.filter_to_result_lines(header_lines, data_from_file, True))
    race_parser.normalize(race_info)
    race_info['id'] = race_id

    return {"race_info": race_info, "results": results}


def add_to_each_row(dictionary_list, extra):
    for row in dictionary_list:
        row.update(extra)


if __name__ == "__main__":
    main()
