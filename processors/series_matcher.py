from collections import defaultdict
import re

SERIES_NAME_PATTERNS_TO_REMOVE = [
    # Year at start of name
    re.compile(r'^2\d{3} '),
    
    # Annual text at start of name
    re.compile(r'^(\d+)(st|nd|rd|th) Annual '),
    
    # Year at end of name
    re.compile(r' 2\d{3}$')
]

def match_series(races):
    # Group races by month, series name, and distance
    grouped_races = defaultdict( list )
    for race in races:
        month = race['date'].month
        series_name = race['name'].strip()
        for pattern in SERIES_NAME_PATTERNS_TO_REMOVE:
            series_name = re.sub(pattern, "", series_name)
        rounded_dist = round(race['dist'], 1)
        key = (month, series_name, rounded_dist)
        
        grouped_races[key].append(race)

    # Create and assign series
    series_id = 1
    series_list = []
    for key in grouped_races:
        month = key[0]
        series_name = key[1]
        rounded_dist = key[2]
        series_list.append({"id": series_id, "name": series_name, "month": month, "dist": rounded_dist})
        series_races = grouped_races[key]
        for race in series_races:
            race['series_id'] = series_id
                
        series_id += 1
    
    return series_list
