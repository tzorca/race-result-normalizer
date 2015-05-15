from containers.state import RaceParseState

DIFF_DIST_RATIO = .25
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
        if not result.get('pace'):
            result['pace'] = time

        this_dist = round(time / result['pace'], 2)

        # Save this distance if no distances have been saved yet
        if len(distances_to_race_ids) == 0:
            distances_to_race_ids[this_dist] = race_parse_state.race_id

        # Save this distance if it is different from the closest existing saved distance
        elif this_dist:

            # Get lowest ratio between saved distance groups and this group
            lowest_diff_ratio = 1
            closest_dist = 0
            for dist in distances_to_race_ids:
                if not dist:
                    continue

                diff_ratio = abs(this_dist - dist) / dist
                if not lowest_diff_ratio or diff_ratio < lowest_diff_ratio:
                    lowest_diff_ratio = diff_ratio
                    closest_dist = dist

            if lowest_diff_ratio > DIFF_DIST_RATIO:
                race_parse_state.race_id += 1
                distances_to_race_ids[this_dist] = race_parse_state.race_id
            else:
                this_dist = closest_dist

        result['race_id'] = distances_to_race_ids[this_dist]


    # Add races
    table_data['race'].clear()
    for dist in distances_to_race_ids:

        # Make a copy of common race info
        race_info = dict(common_race_info)

        # Add the distance and race id to the copy
        race_info
        race_info['dist'] = dist
        race_info['id'] = distances_to_race_ids[dist]

        # Add the race to the race table
        table_data['race'].append(race_info)
