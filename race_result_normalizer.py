import os
import sys
import pymysql
import cProfile
from processors import result_parser, race_parser, runner_matcher
import metrics
from helpers import mysql_helper
from settings import settings
from settings.secure_settings import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_USER
from dateutil.relativedelta import relativedelta

def main():
    if (len(sys.argv) < 2):
        script_name = os.path.basename(__file__)
        print ("Usage: " + script_name + " <directory>")
    else:
        path = sys.argv[1]
        filenames = [os.path.join(path,fn) for fn in os.listdir(path)] 
         
        print("Beginning parse...")
        table_data = parse_files(filenames)
        table_data['runner'] = runner_matcher.match_runners(table_data['result'])
        
        print("Beginning database export...")
        db_connection = pymysql.connect(host=DB_HOST, user=DB_USER, 
                                        passwd=DB_PASSWORD, database=DB_DATABASE, 
                                        charset="utf8")
        for table_name in table_data:
            save_to_db(db_connection, table_data[table_name], settings.TABLE_DEFS[table_name])
        db_connection.close()
  
        metrics.print_error_files()
        print("Finished.")

def save_to_db(db_connection, dataset, table_def):

    mysql_helper.drop_table(db_connection, table_def["name"])
    mysql_helper.create_table(db_connection, table_def)
    mysql_helper.insert_rows(db_connection, table_def, dataset)

def parse_files(filename_list):
    race_id = 1
    table_data = {"race": [], "result": []}

    for filename in filename_list:
        if not filename.endswith(".txt"):
            continue

        file_parse = parse_file(filename, race_id)
        if file_parse:
            for table_name in file_parse:
                table_data[table_name].extend(file_parse[table_name])
        race_id += 1

    return table_data

def parse_file(filename, race_id):
    with open(filename, "r") as input_file:
        data_from_file = input_file.read()

    header_lines = result_parser.get_header(data_from_file)
    if not header_lines:
        metrics.add_error_file(filename, "Could not read header")
        return
    
    race_info = race_parser.get_race_info(result_parser.filter_to_result_lines(header_lines, data_from_file, True))
    race_parser.normalize(race_info)
    race_info['id'] = race_id
    race_info['filename'] = filename
    
    if not len(race_info['name'].strip()):
        metrics.add_error_file(filename, "No race name found")
        return
    
    if not 'date' in race_info:
        metrics.add_error_file(filename, "No race date found")
        return
    
    results = result_parser.get_results(filename, header_lines, data_from_file)
    if not results: 
        return

    add_to_each_row(results, {"race_id":race_id})
    table_data = {"race": [race_info], "result": results}
    rename_columns(table_data, settings.TABLE_DEFS)
    
    # Add "birthdate less than or equal to" field
    for result in results:
        if 'age' in result:
            age = result['age']
            if not age.isdigit():
                continue
            result['birthdate_lte'] = race_info['date'] - relativedelta(years=int(age))

    return table_data

def rename_columns(all_table_data, table_defs):
    for table_name in all_table_data:
        column_renames = table_defs[table_name]['column_renames']
        table_data = all_table_data[table_name]
        for row in table_data:
            for column_name in row:
                value = row[column_name]
                if column_name in column_renames:
                    new_name = column_renames[column_name]
                    row[new_name] = value
                    del row[column_name]


def add_to_each_row(dictionary_list, extra):
    for row in dictionary_list:
        row.update(extra)


if __name__ == "__main__":
    main()
