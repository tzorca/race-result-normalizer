import os
import re
import sqlite3
from datetime import datetime

from dateutil.relativedelta import relativedelta

from helpers import sqlite_helper, logging
from containers.state import RaceParseState
from containers.timer import Timer
from processors import result_parser
from processors import race_parser
from processors import runner_matcher
from processors import series_matcher
from processors import race_distance_splitter
from processors import race_combiner
from processors import stat_field_creater
from processors import runner_name_parser


class RaceResultNormalizer:

    def __init__(self, table_defs, manual_fixes, db_location):
        self.table_defs = table_defs
        self.manual_fixes = manual_fixes
        self.db_location = db_location
        self.EXCLUDED_FILE_DATA_PATTERNS = [
            # Duplicate files
            re.compile(r'^[*]{4} OVERALL .*? [*]{4}$', re.MULTILINE)
        ]

    def normalize_directory(self, input_directory):
        filepaths = [os.path.join(input_directory, fn) for fn in os.listdir(input_directory)]

        self.normalize_files(filepaths)

    def normalize_files(self, filepaths):
        print("Initializing database...")
        with Timer() as t:
            db_connection = sqlite3.connect(self.db_location)

            sqlite_helper.create_table(db_connection, self.table_defs['app_run'])
            sqlite_helper.create_table(db_connection, self.table_defs['log'])

            app_run_id = sqlite_helper.insert_row(db_connection, self.table_defs['app_run'], {"ts": datetime.now()})

        print("... %.02f seconds" % t.interval)

        print("Parsing files...")
        with Timer() as t:
            table_data = self.parse_files(filepaths)
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
            self.export_to_db(db_connection, table_data, app_run_id)

        print("... %.02f seconds" % t.interval)

        for table_name in table_data:
            record_count = len(table_data[table_name])
            print(table_name + ": " + str(record_count))

        print("Finished.")

    def export_to_db(self, db_connection, table_data, app_run_id):
        for table_name in table_data:
            self.save_to_db(db_connection, table_data[table_name], self.table_defs[table_name])

        sqlite_helper.run_commands(db_connection, self.manual_fixes)

        self.save_log_entries(db_connection, logging.log_entries, app_run_id)

        db_connection.close()

    def save_log_entries(self, db_connection, log_entries, app_run_id):
        for entry in log_entries:
            entry['app_run_id'] = app_run_id

        sqlite_helper.insert_rows(db_connection, self.table_defs["log"], log_entries)

    def save_to_db(self, db_connection, dataset, table_def):
        sqlite_helper.drop_table(db_connection, table_def["name"])
        sqlite_helper.create_table(db_connection, table_def)
        sqlite_helper.insert_rows(db_connection, table_def, dataset)

    def parse_files(self, filename_list):
        race_parse_state = RaceParseState("", 1)
        table_data = {"race": [], "result": []}

        for filename in filename_list:
            if not filename.endswith(".txt"):
                continue

            race_parse_state.filename = filename
            file_parse = self.parse_file(race_parse_state)
            if file_parse:
                for table_name in file_parse:
                    table_data[table_name].extend(file_parse[table_name])
                race_parse_state.race_id += 1

        return table_data

    def parse_file(self, race_parse_state):
        filename = race_parse_state.filename
        with open(filename, "r") as input_file:
            data_from_file = input_file.read()

        for pattern in self.EXCLUDED_FILE_DATA_PATTERNS:
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
        self.rename_columns(file_table_data, self.table_defs)

        self.add_birthdate_lte(file_table_data)
        race_distance_splitter.assign_distances_and_race_ids(race_parse_state, file_table_data)

        return file_table_data

    def rename_columns(self, all_table_data, table_defs):
        for table_name in all_table_data:
            column_renames = table_defs[table_name]['column_renames']
            table_data = all_table_data[table_name]
            for row in table_data:
                for old_name in column_renames:
                    if old_name in row:
                        new_name = column_renames[old_name]
                        row[new_name] = row.pop(old_name)

    def add_birthdate_lte(self, table_data):
        race_info = table_data['race'][0]
        for result in table_data['result']:
            if 'age' in result:
                age = result['age']
                if not age.isdigit():
                    continue
                result['birthdate_lte'] = race_info['date'] - relativedelta(years=int(age))
