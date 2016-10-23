import re
from helpers import field_normalizers, logging
from settings import settings


RESULTS_HEADER_SEPARATOR_PATTERN = re.compile(r'(=+ ?)+')


def get_results(filename, header_lines, data_from_file):
    field_defs = get_field_defs(header_lines)

    result_lines = filter_to_result_lines(header_lines, data_from_file, False)
    mapped_results = map_results(field_defs, result_lines)

    if filter_bad_resultset(filename, mapped_results):
        return None

    normalize(mapped_results, filename)
    mapped_results = remove_bad_results(filename, mapped_results)

    return mapped_results


def get_header(raw_data):
    header_lines = None

    line_num = 0
    lines = raw_data.splitlines(True)
    for line in lines:
        match = RESULTS_HEADER_SEPARATOR_PATTERN.match(line)

        if match:
            header_lines = [lines[line_num - 1], line]
            break

        line_num += 1

    return header_lines


def get_field_defs(header_lines):
    field_defs = []
    new_field = {'start': 0}

    # TODO: This currently relies on a space being at the end of the header
    for i, c in enumerate(header_lines[1]):
        if c == " ":
            new_field['end'] = i
            field_defs.append(new_field)

            new_field = {'start': i + 1}

    for field in field_defs:
        start = field['start']
        end = field['end']

        field['name'] = header_lines[0][start:end].strip()

    return field_defs


def filter_to_result_lines(header_lines, raw_data, invert: bool):
    lines = raw_data.splitlines(True)
    good_lengths = list(map(len, header_lines))

    result_lines = []

    past_header = False

    for line in lines:
        # Skip header lines (Even when inverting)
        if any(line == header for header in header_lines):
            past_header = True
            continue

        # Don't claim lines as results until after the header 
        if not invert and not past_header:
            continue

        # Skip lines whose length doesn't equal the header line's length
        if any(len(line) == good_length for good_length in good_lengths) == invert:
            continue

        result_lines.append(line)

    return result_lines


def map_results(field_defs, result_lines):
    mapped_results = []

    for line in result_lines:
        mapped_result = {}

        for field_def in field_defs:
            name = field_def['name']
            start = field_def['start']
            end = field_def['end']

            mapped_result[name] = line[start:end].strip()

        mapped_results.append(mapped_result)

    return mapped_results



def normalize(mapped_results, filename):
    for row in mapped_results:
        for time_field in settings.RESULT_TIME_COLUMN_NAMES:
            if time_field in row:
                time = None
                try:
                    time = field_normalizers.time_string_to_minutes_decimal(row[time_field])
                except Exception as e:
                    logging.log_error(
                        filename=filename,
                        category='Could not parse time string',
                        details=str(e)
                    )

                if time:
                    row[time_field] = round(time, 1)
                else:
                    row[time_field] = None
    return mapped_results


BLANK_CUTOFF_RATIO = 0.05


def filter_bad_resultset(filename, resultset):
    if not resultset or len(resultset) == 0:
        logging.log_error(filename=filename, category="No result entries found", details="")
        return True

    return False


def remove_bad_results(filename, resultset):
    output_resultset = []
    for result in resultset:
        name = result.get('Name')
        if not name or len(name) == 0:
            logging.log_error(filename=filename, category="Blank name", details="")
            continue

        if '**' in name:
            logging.log_error(filename=filename, category="Invalid name", details=name)
            continue

        has_finish_time = False
        for time_col_name in settings.RESULT_TIME_COLUMN_NAMES:
            if result.get(time_col_name):
                has_finish_time = True
        
        if not has_finish_time:
            logging.log_error(filename=filename, category="Missing finish time", details="Name = " + name)
            continue

        output_resultset.append(result)
    return output_resultset
