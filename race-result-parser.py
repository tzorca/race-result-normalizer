import os
import re

RESULTS_HEADER_SEPARATOR_PATTERN = re.compile(r'(=+ ?)+')

def parse_results(data):
    lines = data.splitlines(True)
    for line in lines:
        match = RESULTS_HEADER_SEPARATOR_PATTERN.match(line)

        if (match is not None):
            print(match.group())


DATA_DIRECTORY = "./data/"
for filename in os.listdir(DATA_DIRECTORY):
    with open(DATA_DIRECTORY + filename, "r") as f:
        parse_results(f.read())






