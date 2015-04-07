import re
import time
from datetime import datetime

STATE = "(Tennessee|TN|Georgia|GA|Alabama|AL|North Carolina|NC|Florida|FL)"
MONTH = "(January|February|March|April|May|June|July|August|September|October|November|December)"
YEAR = r'2\d{3}'
DIST_UNIT = "(kilometer|k|miler|miles|mile|mi)"

ALL_PATTERN = re.compile('.*')
TIME_PATTERN = re.compile(r'\d{1,2}:\d{2} ?(A|P)M')
DATE_PATTERN = re.compile(MONTH + r' ?\d+, ?' + YEAR)
LOCATION_PATTERN = re.compile(r'^\s*([A-Za-z ]{3,}, ){1,3}' + STATE)
CERTIFICATION_PATTERN = re.compile(r'(?<=\().*(?=\))')

PAREN_BLOCK_PATTERN = re.compile(r'\(.*?\)')

EXCLUDED_PATTERNS = [
    # Page Number
    re.compile(r'^\s*page \d+$', re.IGNORECASE),
    
    # Blank line
    re.compile(r'^\s+$')
]

# Outer array has patterns for line matching
# Components have patterns for matching actual race information pieces within a line
RACE_INFO_PATTERNS = [
    {
        'name': 'date_time',
        'pattern': DATE_PATTERN,
        'components': [
            {'name':'date', 'pattern': DATE_PATTERN},
            {'name':'time', 'pattern': TIME_PATTERN}
        ]
    },
    {
        'name': 'location',
        'pattern': LOCATION_PATTERN,
        'components': [
            {'name':'location', 'pattern': LOCATION_PATTERN},
            {'name':'certification', 'pattern': CERTIFICATION_PATTERN}
        ]
    },
]

def is_relevant_race_line(line):
    return not any(pattern.match(line) is not None for pattern in EXCLUDED_PATTERNS)

def get_race_info(non_result_lines):
    matched_lines = []
    race_info = {}

    race_info_lines = filter(is_relevant_race_line, non_result_lines)

    for line in race_info_lines:
        line_matched = False
        
        for line_breakdown in RACE_INFO_PATTERNS:
            line_name = line_breakdown['name']
            if line_breakdown['pattern'].search(line):
                line_matched = True

                if line_name not in matched_lines:
                    matched_lines.append(line_name)

                for component in line_breakdown['components']:
                    match = component['pattern'].search(line)
                    if match:
                        race_info[component['name']] = match.group(0).strip()
                break

        if not line_matched and "name" not in race_info:
            # The race name line should be the first line after filtering out the above
            race_info["name"] = line.strip()
        
    # Remove unimportant parenthetical information
    # (Important information will have already been captured)
    for info_name in race_info:
        race_info[info_name] = PAREN_BLOCK_PATTERN.sub('', race_info[info_name])

    return race_info


DATE_FORMATS = ["%B %d, %Y", "%B %d,%Y"]
TIME_FORMATS = ["%I:%M %p", "%I:%M%p"]


def normalize(race_info):
    if ('date' in race_info):
        date_str = race_info['date']
        race_info['date'] = None
        for date_format in DATE_FORMATS:
            try:
                race_info['date'] = datetime.strptime(date_str, date_format)
            except ValueError:
                pass
            else:
                break

    if ('time' in race_info):
        time_str = race_info['time']
        race_info['time'] = None
        for time_format in TIME_FORMATS:
            try:
                race_info['time'] = time.strptime(time_str, time_format)
            except ValueError:
                pass
            else:
                break

