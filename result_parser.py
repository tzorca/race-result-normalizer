import re

RESULTS_HEADER_SEPARATOR_PATTERN = re.compile(r'(=+ ?)+')

STATES = "(Tennessee|TN|Georgia|GA|Alabama|AL|North Carolina|NC|Florida|FL)"
MONTHS = "(January|February|March|April|May|June|July|August|September|October|November|December)"
YEAR = r'2\d{3}'
DIST_UNITS = "(kilometer|k|miler|miles|mile|mi)"

TIME_PATTERN = re.compile(r'\d{2}:\d{2} (A|P)M')

EXCLUDED_PATTERNS = [
    # Page Number
    re.compile(r'^\s*page \d+$', re.IGNORECASE)
]


RACE_INFO_PATTERNS = {
    'date': re.compile(MONTHS + r' ?\d+, ?' + YEAR),
    'location': re.compile(r'^\s*[A-Za-z ]{3,}, ' + STATES + r'.*$')
}

def is_relevant_race_line(line):
    return not any(pattern.match(line) is not None for pattern in EXCLUDED_PATTERNS)

def get_race_info(non_result_lines):
    info_lines = {}
    
    race_info_lines = filter(is_relevant_race_line, non_result_lines)
    
    for line in race_info_lines:
        pattern_matched = False
        for pattern_name, pattern in RACE_INFO_PATTERNS.items():
            if pattern.search(line) is not None:
                pattern_matched = True
                if pattern_name not in info_lines:
                    info_lines[pattern_name] = line
                break
        
        if not pattern_matched and "name" not in info_lines:
            # The race name line should be the first line after filtering out the above
            info_lines["name"] = line
        
    race_info = {}
    return race_info

def parse_results(raw_data):
    header_lines = get_header(raw_data)
    field_defs = get_field_defs(header_lines)
    result_lines = filter_to_result_lines(header_lines, raw_data, False)
    mapped_results= get_mapped_results(field_defs, result_lines)
    race_info = get_race_info(filter_to_result_lines(header_lines, raw_data, True))
    
    return {"race_info": race_info, "results": mapped_results}

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


def filter_to_result_lines(header_lines, raw_data, invert: bool):
    lines = raw_data.splitlines(True)
    good_lengths = list(map(len, header_lines))
        
    result_lines = []

    for line in lines:
        # Skip header lines (Even when inverting)
        if (any(line == header for header in header_lines)):
            continue

        # Skip lines whose length doesn't equal the header line's length
        if (any(len(line) == good_length for good_length in good_lengths) == invert):
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

    
    
    
    
    
    