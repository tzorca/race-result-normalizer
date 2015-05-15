from containers.state import RaceParseState
from helpers import data_helper
from metrics import metrics

MIN_PERCENT_DIFF_FOR_NEW_DIST = .25
def assign_distances_and_race_ids(race_parse_state: RaceParseState, table_data):
    results = table_data['result']
    common_race_info = table_data['race'][0]

    # Assign distances and get race ID for each distance
    distances_to_race_ids = {}
    for result in results:

        time = result.get('gun_time') or result.get('net_time')
        
        # Skip results without times
        if not time:
            continue

        # If no pace exists, assume pace is the same as the time
        result['pace'] = result.get('pace') or time

        # Calculate distance to the nearest .1
        this_dist = round(time / result['pace'], 1)
        
        if not this_dist:
            metrics.add_error("Race distance calculated as null.", race_parse_state.filename)

        if len(distances_to_race_ids) == 0:
            distances_to_race_ids[this_dist] = race_parse_state.race_id
        else:
            closest_dist = data_helper.lowest_percent_diff_element(distances_to_race_ids, this_dist)
            closest_percent_diff = data_helper.get_abs_percent_diff(this_dist, closest_dist)

            if closest_percent_diff > MIN_PERCENT_DIFF_FOR_NEW_DIST:
                race_parse_state.race_id += 1
                distances_to_race_ids[this_dist] = race_parse_state.race_id
            else: # Converge this distance to the closest if not significantly different
                this_dist = closest_dist

        result['race_id'] = distances_to_race_ids[this_dist]

    # Add races
    table_data['race'].clear()
    for dist in distances_to_race_ids:
        race_specific_info = {'dist': dist, 'id': distances_to_race_ids[dist]}

        table_data['race'].append(dict(common_race_info, **race_specific_info))
