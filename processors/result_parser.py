import re
import metrics
from helpers import field_normalizers, data_helper

RESULTS_HEADER_SEPARATOR_PATTERN = re.compile(r'(=+ ?)+')

def get_results(filename, header_lines, data_from_file):
    field_defs = get_field_defs(header_lines)

    result_lines = filter_to_result_lines(header_lines, data_from_file, False)
    mapped_results = map_results(field_defs, result_lines)

    if filter_bad_resultset(filename, mapped_results):
        return None
    
    normalize(mapped_results)
    
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
    new_field = {'start':0}

    # TODO: This currently relies on a space being at the end of the header
    for i, c in enumerate(header_lines[1]):
        if (c == " "):
            new_field['end'] = i
            field_defs.append(new_field)

            new_field = {'start':i + 1}

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
        if (any(line == header for header in header_lines)):
            past_header = True
            continue
        
        # Don't claim lines as results until after the header 
        if not invert and not past_header:
            continue

        # Skip lines whose length doesn't equal the header line's length
        if (any(len(line) == good_length for good_length in good_lengths) == invert):
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

TIME_FIELDS = ["Time", "Guntime", "Nettime", "Pace"]

def normalize(mapped_results):
    for row in mapped_results:
        for time_field in TIME_FIELDS:
            if time_field in row:
                row[time_field] = field_normalizers.time_string_to_minutes_decimal(row[time_field])
    return mapped_results


BLANK_CUTOFF_RATIO = 0.05
def filter_bad_resultset(filename, resultset):
    if (not resultset or len(resultset) == 0):
        metrics.add_error(filename, "No result entries found")
        return True

    blank_name_ratio = data_helper.get_blank_ratio(resultset, "Name")
    if (blank_name_ratio > BLANK_CUTOFF_RATIO):        
        metrics.add_error(filename, "blank_name_ratio > BLANK_CUTOFF_RATIO")
        return True

    return False



