import os
import sys
import pymysql
import re
from metrics import metrics
from containers.timer import Timer
from containers.state import RaceParseState
from helpers import mysql_helper
from processors import result_parser, race_parser, runner_matcher, \
    series_matcher, race_distance_splitter, race_combiner, stat_field_creater
from settings import settings, manual_fixes
from settings.secure_settings import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_USER
from dateutil.relativedelta import relativedelta

def main():
    if (len(sys.argv) < 2):
        script_name = os.path.basename(__file__)
        print ("Usage: " + script_name + " <directory>")
    else:
        path = sys.argv[1]
        filenames = [os.path.join(path, fn) for fn in os.listdir(path)]

        print("Parsing files...")
        with Timer() as t:
            table_data = parse_files(filenames)
        print("... %.02f seconds" % t.interval)
        
        print('Combining same races...')
        with Timer() as t:
            race_combiner.combine_same_races(table_data)
        print("... %.02f seconds" % t.interval)
        
        print('Matching runners...')
        with Timer() as t:
            table_data['runner'] = runner_matcher.match_runners(table_data['result'])
        print("... %.02f seconds" % t.interval)
        
        print('Matching series...')
        with Timer() as t:
            table_data['series'] = series_matcher.match_series(table_data['race'])
        print("... %.02f seconds" % t.interval)
        
        print('Adding percentile field...')
        with Timer() as t:
            stat_field_creater.add_percentile_field(table_data['result'])
        print("... %.02f seconds" % t.interval)
        
        print("Exporting to database...")
        with Timer() as t:
            db_connection = pymysql.connect(host=DB_HOST, user=DB_USER,
                passwd=DB_PASSWORD, database=DB_DATABASE, charset="utf8")
            
            for table_name in table_data:
                save_to_db(db_connection, table_data[table_name], settings.TABLE_DEFS[table_name])

            mysql_helper.run_commands(db_connection, manual_fixes.fixes)

            db_connection.close()
        print("... %.02f seconds" % t.interval)

        metrics.print_errors()
        print("Finished.")


def save_to_db(db_connection, dataset, table_def):
    mysql_helper.drop_table(db_connection, table_def["name"])
    mysql_helper.create_table(db_connection, table_def)
    mysql_helper.insert_rows(db_connection, table_def, dataset)


EXCLUDED_FILE_DATA_PATTERNS = [
    # Duplicate files
    re.compile(r'^[*]{4} OVERALL .*? [*]{4}$', re.MULTILINE)
]

def parse_files(filename_list):
    race_parse_state = RaceParseState("", 1)
    table_data = {"race": [], "result": []}

    for filename in filename_list:
        if not filename.endswith(".txt"):
            continue
        
        race_parse_state.filename = filename
        file_parse = parse_file(race_parse_state)
        if file_parse:
            for table_name in file_parse:
                table_data[table_name].extend(file_parse[table_name])
            race_parse_state.race_id += 1

    return table_data


def parse_file(race_parse_state):
    filename = race_parse_state.filename
    with open(filename, "r") as input_file:
        data_from_file = input_file.read()

    for pattern in EXCLUDED_FILE_DATA_PATTERNS:
        if pattern.search(data_from_file):
            metrics.add_error(filename, "Excluded file data pattern: " + str(pattern))
            return

    header_lines = result_parser.get_header(data_from_file)
    if not header_lines:
        metrics.add_error(filename, "Could not read header")
        return

    race_info = race_parser.get_race_info(result_parser.filter_to_result_lines(header_lines, data_from_file, True))
    race_parser.normalize(race_info)

    race_info['filename'] = filename

    if not len(race_info['name'].strip()):
        metrics.add_error(filename, "No race name found")
        return

    if not 'date' in race_info:
        metrics.add_error(filename, "No race date found")
        return

    results = result_parser.get_results(filename, header_lines, data_from_file)
    if not results:
        return

    file_table_data = {"race": [race_info], "result": results}
    rename_columns(file_table_data, settings.TABLE_DEFS)

    add_birthdate_lte(file_table_data)
    race_distance_splitter.assign_distances_and_race_ids(race_parse_state, file_table_data)

    return file_table_data


def rename_columns(all_table_data, table_defs):
    for table_name in all_table_data:
        column_renames = table_defs[table_name]['column_renames']
        table_data = all_table_data[table_name]
        for row in table_data:
            for old_name in row:
                if old_name in column_renames:
                    new_name = column_renames[old_name]
                    row[new_name] = row.pop(old_name)


def add_birthdate_lte(table_data):
    race_info = table_data['race'][0]
    for result in table_data['result']:
        if 'age' in result:
            age = result['age']
            if not age.isdigit():
                continue
            result['birthdate_lte'] = race_info['date'] - relativedelta(years=int(age))


if __name__ == "__main__":
    main()
