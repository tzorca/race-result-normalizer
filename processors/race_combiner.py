from metrics import metrics
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
            id_remappings[race['id']] = new_race_id
    
    for result in table_data['result']:
        if not 'race_id' in result:
            metrics.add_error("", "No race_id in result")
            continue
        orig_race_id = result['race_id']
        
        if not orig_race_id in id_remappings:
            metrics.add_error(orig_race_id, "No remapping exists for race_id")
            continue
        result['race_id'] = id_remappings[orig_race_id]
    
    table_data['race'] = new_races