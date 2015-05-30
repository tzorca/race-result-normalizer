import re

SERIES_NAME_PATTERNS_TO_REMOVE = [
    # Space at end of name
    re.compile(r' +$'),
                                  
    # Year at start of name
    re.compile(r'^2\d{3} '),
    
    # Year at end of name
    re.compile(r' 2\d{3}$'),
    
    # Annual text
    re.compile(r'(\d+)(st|nd|rd|th) Annual ', re.IGNORECASE),
    
    # Commas
    re.compile(r',')
]

def match_series(races):
    # Group races by month, series code name, and distance
    grouped_races = {}
    for race in races:
        month = race['date'].month
        
        series_human_name = create_series_human_name(race['name'])
        series_code_name = codify_series_name(series_human_name)
        
        rounded_dist = round(race['dist'], 1)
        key = (month, series_code_name, rounded_dist)
        
        if key in grouped_races:
            grouped_races[key]['races'].append(race)
        else:
            grouped_races[key] = {
                'races': [race],
                'human_name': series_human_name
            }

    # Create and assign series
    series_id = 1
    series_list = []
    for key in grouped_races:
        month = key[0]
        dist = key[2]
        human_name = grouped_races[key]['human_name']
        series_list.append({"id": series_id, "name": human_name, "month": month, "dist": dist})
        series_races = grouped_races[key]['races']
        for race in series_races:
            race['series_id'] = series_id
                
        series_id += 1
    
    return series_list


def create_series_human_name(race_name):
    series_human_name = race_name
    for pattern in SERIES_NAME_PATTERNS_TO_REMOVE:
        series_human_name = re.sub(pattern, "", series_human_name)
    
    return series_human_name.strip()


NUM_WORDS_TO_MATCH = 3
def codify_series_name(series_human_name):
    series_code_name_words = series_human_name.lower().split()[:NUM_WORDS_TO_MATCH]
    
    return ' '.join(series_code_name_words)
