import os
import re

RESULTS_HEADER_SEPARATOR_PATTERN = re.compile(r'(=+ ?)+')

NON_RESULT_PATTERNS = [
    re.compile(r'\*{4,}'),
    re.compile(r' {30,}')
]

def parse_results(raw_data):
    header_lines = get_header(raw_data)
    field_defs = get_field_defs(header_lines)
    result_lines = filter_to_result_lines(header_lines, raw_data)

    return get_mapped_results(field_defs, result_lines)

def get_header(raw_data):
    header_lines = None

    line_num = 0
    lines = raw_data.splitlines(True)
    for line in lines:
        match = RESULTS_HEADER_SEPARATOR_PATTERN.match(line)

        if (match is not None):
            header_lines = [lines[line_num-1], line]
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

            new_field = {'start':i+1}

    for field in field_defs:
        start = field['start']
        end = field['end']

        field['name'] = header_lines[0][start:end].strip()

    return field_defs

def filter_to_result_lines(header_lines, raw_data):
    lines = raw_data.splitlines(True)
    good_lengths = map(len, header_lines)
    result_lines = []

    for line in lines:

        # Skip header lines
        if (any(line == header for header in header_lines)):
            continue

        # Skip lines whose length doesn't equal the header line's length
        if (not any(len(line) == good_length for good_length in good_lengths)):
            continue

        # Skip lines matching known non-results patterns
        if (any(pattern.search(line) != None for pattern in NON_RESULT_PATTERNS)):
            continue

        result_lines.append(line)

    return result_lines

def get_mapped_results(field_defs, result_lines):
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

DATA_DIRECTORY = "./data/"
for filename in os.listdir(DATA_DIRECTORY):
    with open(DATA_DIRECTORY + filename, "r") as f:
        lst = parse_results(f.read())
        print lst


