import os
import sys
import pymysql
import re
import metrics
from collections import defaultdict
from helpers import mysql_helper
from processors import result_parser, race_parser, runner_matcher, \
    series_matcher
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

        print("Beginning parse...")
        table_data = parse_files(filenames)
        table_data['runner'] = runner_matcher.match_runners(table_data['result'])
        table_data['series'] = series_matcher.match_series(table_data['race'])

        print("Beginning database export...")
        db_connection = pymysql.connect(host=DB_HOST, user=DB_USER,
                                        passwd=DB_PASSWORD, database=DB_DATABASE,
                                        charset="utf8")
        for table_name in table_data:
            save_to_db(db_connection, table_data[table_name], settings.TABLE_DEFS[table_name])

        mysql_helper.run_commands(db_connection, manual_fixes.fixes)

        db_connection.close()

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

current_race_id = 1
def parse_files(filename_list):
    global current_race_id
    table_data = {"race": [], "result": []}

    for filename in filename_list:
        if not filename.endswith(".txt"):
            continue

        file_parse = parse_file(filename)
        if file_parse:
            for table_name in file_parse:
                table_data[table_name].extend(file_parse[table_name])
        current_race_id += 1

    combine_same_races(table_data)

    return table_data

def combine_same_races(table_data):
    same_race_groups = defaultdict(list)
    for race in table_data['race']:
        key = (
            race.get('name'),
            race.get('date'),
            race.get('location'),
            race.get('dist')
        )
        same_race_groups[key].append(race)
    
    id_remappings = {}
    new_race_id = 1
    new_races = []
    for same_race_key in same_race_groups:
        same_race_group = same_race_groups[same_race_key]
        same_race_group[0]['id'] = new_race_id
        new_races.append(same_race_group[0])
        for race in same_race_group:
            id_remappings[race['id']] = new_race_id
        
        new_race_id += 1
    
    for result in table_data['result']:
        if not 'race_id' in result:
            metrics.add_error("", "No race_id in result")
            continue
        orig_race_id = result['race_id']
        if orig_race_id in id_remappings:
            result['race_id'] = id_remappings[orig_race_id]
    
    table_data['race'] = new_races


DIFF_DIST_RATIO = .25
def parse_file(filename):
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

    table_data = {"race": [race_info], "result": results}
    rename_columns(table_data, settings.TABLE_DEFS)

    add_birthdate_lte(table_data)
    assign_distances_and_race_ids(table_data)

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


def add_birthdate_lte(table_data):
    race_info = table_data['race'][0]
    for result in table_data['result']:
        if 'age' in result:
            age = result['age']
            if not age.isdigit():
                continue
            result['birthdate_lte'] = race_info['date'] - relativedelta(years=int(age))

def assign_distances_and_race_ids(table_data):
    global current_race_id
    results = table_data['result']
    common_race_info = table_data['race'][0]

    # Assign distances and get race ID for each distance
    distances_to_race_ids = {}
    for result in results:

        time = result.get('gun_time') or result.get('net_time')
        if not time:
            # Skip results without times
            continue

        # If no pace exists, assume pace is the same as the time
        if not result.get('pace'):
            result['pace'] = time

        this_dist = round(time / result['pace'], 2)

        # Save this distance if no distances have been saved yet
        if len(distances_to_race_ids) == 0:
            distances_to_race_ids[this_dist] = current_race_id

        # Save this distance if it is different from the closest existing saved distance
        elif this_dist:

            # Get lowest ratio between saved distance groups and this group
            lowest_diff_ratio = 1
            closest_dist = 0
            for dist in distances_to_race_ids:
                if not dist:
                    continue

                diff_ratio = abs(this_dist - dist) / dist
                if not lowest_diff_ratio or diff_ratio < lowest_diff_ratio:
                    lowest_diff_ratio = diff_ratio
                    closest_dist = dist

            if lowest_diff_ratio > DIFF_DIST_RATIO:
                current_race_id += 1
                distances_to_race_ids[this_dist] = current_race_id
            else:
                this_dist = closest_dist

        result['race_id'] = distances_to_race_ids[this_dist]

    # Add races
    table_data['race'].clear()
    for dist in distances_to_race_ids:

        # Make a copy of common race info
        race_info = dict(common_race_info)

        # Add the distance and race id to the copy
        race_info['dist'] = dist
        race_info['id'] = distances_to_race_ids[dist]

        # Add the race to the race table
        table_data['race'].append(race_info)

if __name__ == "__main__":
    main()
