import os
import re

RESULTS_HEADER_SEPARATOR_PATTERN = re.compile(r'(=+ ?)+')
NON_SPACE = re.compile(r'\S')


def parse_results(data):
    header_lines = get_header(data)
    header_fields = interpret_header(header_lines)

    print header_lines

def get_header(data):
    header_lines = None

    line_num = 0
    lines = data.splitlines(True)
    for line in lines:
        match = RESULTS_HEADER_SEPARATOR_PATTERN.match(line)

        if (match is not None):
            header_lines = [lines[line_num-1], line]
            break

        line_num += 1

    return header_lines


# Place Name                     Bib#  Age S Guntime  Pace     
# ===== ======================== ===== === = =======  ===== 
def interpret_header(header_lines):
    # Find start and end of every non-space character
    


DATA_DIRECTORY = "./data/"
for filename in os.listdir(DATA_DIRECTORY):
    with open(DATA_DIRECTORY + filename, "r") as f:
        parse_results(f.read())






