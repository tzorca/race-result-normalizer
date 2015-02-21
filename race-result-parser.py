import os
import re

RESULTS_HEADER_SEPARATOR_PATTERN = re.compile(r'(=+ ?)+')

def parse_results(raw_data):
    header_lines = get_header(raw_data)
    field_defs = get_field_defs(header_lines)

    print fields

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


# Place Name                     Bib#  Age S Guntime  Pace     
# ===== ======================== ===== === = =======  ===== 
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

DATA_DIRECTORY = "./data/"
for filename in os.listdir(DATA_DIRECTORY):
    with open(DATA_DIRECTORY + filename, "r") as f:
        parse_results(f.read())






