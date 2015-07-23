from helpers import logging
from collections import defaultdict

def combine_same_races(table_data):
    same_race_groups = defaultdict(list)
    for race in table_data['race']:
        key = (
            race.get('name'),
            race.get('date'),
            race.get('dist')
        )
        same_race_groups[key].append(race)
    
    id_remappings = {}
    new_races = []
    for same_race_key in same_race_groups:
        same_race_group = same_race_groups[same_race_key]
        new_race_id = same_race_group[0]['id']
        new_races.append(same_race_group[0])
        for race in same_race_group:
            race_id = race['id']
            id_remappings[race_id] = new_race_id
    
    for result in table_data['result']:
        if not 'race_id' in result:
            logging.log_error(filename="", category="No race_id in result", details=result['id'])
            continue
        orig_race_id = result['race_id']
        
        if not orig_race_id in id_remappings:
            logging.log_error(filename="", category="No remapping exists for race_id", details=orig_race_id)
            continue
        result['race_id'] = id_remappings[orig_race_id]
    
    table_data['race'] = new_races
