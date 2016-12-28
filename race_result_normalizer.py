import os
import re
import sqlite3
import sys
from datetime import datetime

from dateutil.relativedelta import relativedelta

from containers.state import RaceParseState
from containers.timer import Timer
from helpers import sqlite_helper, logging
from processors import result_parser, race_parser, runner_matcher, \
    series_matcher, race_distance_splitter, race_combiner, \
    stat_field_creater, runner_name_parser
from settings import settings, secure_settings, manual_fixes


def main():
    if len(sys.argv) < 2:
        script_name = os.path.basename(__file__)
        print("Usage: " + script_name + " <directory>")
    else:
        path = sys.argv[1]
        filenames = [os.path.join(path, fn) for fn in os.listdir(path)]

        print("Initializing database...")
        with Timer() as t:
            db_connection = sqlite3.connect(secure_settings.DB_LOCATION)

            sqlite_helper.create_table(db_connection, settings.TABLE_DEFS['app_run'])
            sqlite_helper.create_table(db_connection, settings.TABLE_DEFS['log'])

            app_run_id = sqlite_helper.insert_row(db_connection, settings.TABLE_DEFS['app_run'], {"ts": datetime.now()})

        print("... %.02f seconds" % t.interval)

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

        print('Adding percentile field to results...')
        with Timer() as t:
            stat_field_creater.add_percentile_field(table_data['result'])
        print("... %.02f seconds" % t.interval)

        print('Parsing runner names into components')
        with Timer() as t:
            runner_name_parser.add_name_component_fields(table_data['runner'])
        print("... %.02f seconds" % t.interval)

        print("Exporting to database...")
        with Timer() as t:
            # pr = cProfile.Profile()
            # pr.enable()
            export_to_db(db_connection, table_data, app_run_id)
            # pr.disable()
            # s = StringIO()
            # sortby = 'cumtime'
            # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            # ps.print_stats()
            # print(s.getvalue())

        print("... %.02f seconds" % t.interval)

        for table_name in table_data:
            record_count = len(table_data[table_name])
            print(table_name + ": " + str(record_count))

        print("Finished.")


def export_to_db(db_connection, table_data, app_run_id):
    for table_name in table_data:
        save_to_db(db_connection, table_data[table_name], settings.TABLE_DEFS[table_name])

    sqlite_helper.run_commands(db_connection, manual_fixes.fixes)

    save_log_entries(db_connection, logging.log_entries, app_run_id)

    db_connection.close()


def save_log_entries(db_connection, log_entries, app_run_id):
    for entry in log_entries:
        entry['app_run_id'] = app_run_id

    sqlite_helper.insert_rows(db_connection, settings.TABLE_DEFS["log"], log_entries)


def save_to_db(db_connection, dataset, table_def):
    sqlite_helper.drop_table(db_connection, table_def["name"])
    sqlite_helper.create_table(db_connection, table_def)
    sqlite_helper.insert_rows(db_connection, table_def, dataset)


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
            logging.log_info(filename=filename, category="Excluded file data pattern", details=str(pattern))
            return

    header_lines = result_parser.get_header(data_from_file)
    if not header_lines:
        logging.log_error(filename=filename, category="Could not read header", details="")
        return

    race_info = race_parser.get_race_info(result_parser.filter_to_result_lines(header_lines, data_from_file, True))
    race_parser.normalize(race_info)

    race_info['filename'] = filename

    if not len(race_info['name'].strip()):
        logging.log_error(filename=filename, category="No race name found", details="")
        return

    if 'date' not in race_info:
        logging.log_error(filename=filename, category="No race date found", details="")
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
            for old_name in column_renames:
                if old_name in row:
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
