import re

STATES = "(Tennessee|TN|Georgia|GA|Alabama|AL|North Carolina|NC|Florida|FL)"
MONTHS = "(January|February|March|April|May|June|July|August|September|October|November|December)"
YEAR = r'2\d{3}'
DIST_UNITS = "(kilometer|k|miler|miles|mile|mi)"

ALL_PATTERN = re.compile('.*')
TIME_PATTERN = re.compile(r'\d{1,2}:\d{2} ?(A|P)M')
DATE_PATTERN = re.compile(MONTHS + r' ?\d+, ?' + YEAR)
LOCATION_PATTERN = re.compile(r'^\s*[A-Za-z ]{3,}, ' + STATES + r'.*$')

EXCLUDED_PATTERNS = [
    # Page Number
    re.compile(r'^\s*page \d+$', re.IGNORECASE)
]

# Outer array has patterns for line matching
# Components have patterns for matching actual race information pieces within a line
RACE_INFO_PATTERNS = [
    {
        'name':'date_time',
        'pattern': DATE_PATTERN,
        'components': [
            {'name':'date', 'pattern': DATE_PATTERN},
            {'name':'time', 'pattern': TIME_PATTERN}
        ]
    },
    {
        'name':'location',
        'pattern': LOCATION_PATTERN,
        'components': [
            {'name':'location', 'pattern': LOCATION_PATTERN}
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
        
        if not line_matched and "race_name" not in race_info:
            # The race name line should be the first line after filtering out the above
            race_info["race_name"] = line.strip()
        
    return race_info
