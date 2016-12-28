from containers.state import RaceParseState
from helpers import data_helper
from collections import defaultdict
import numpy as np

MIN_PERCENT_DIFF_FOR_NEW_DIST = .25


def assign_distances_and_race_ids(state: RaceParseState, table_data):
    dist_grouped_results = group_by_distance(table_data['result'],
                                             MIN_PERCENT_DIFF_FOR_NEW_DIST)

    common_race_info = table_data['race'][0]

    table_data['race'].clear()
    for dist_group in dist_grouped_results:
        dist_specific_results = dist_grouped_results[dist_group]

        all_distances = [r['dist'] for r in dist_specific_results if r.get('dist')]
        if len(all_distances) > 0:
            real_dist = round(float(np.mean(all_distances)), 1)
        else:
            real_dist = None

        for result in dist_specific_results:
            result['race_id'] = state.race_id

        race_specific_info = {'dist': real_dist, 'id': state.race_id}
        table_data['race'].append(dict(common_race_info, **race_specific_info))

        state.race_id += 1


def group_by_distance(results, dist_grouping_percent_diff):
    dist_grouped_results = defaultdict(list)
    for result in results:

        time = result.get('gun_time') or result.get('net_time')

        # Results without times go to the None distance group
        if not time:
            dist_grouped_results[None].append(result)
            continue

        # If no pace exists, don't set pace
        result['pace'] = result.get('pace') or None

        if result['pace']:
            result['dist'] = time / result['pace']
        else:
            result['Dist'] = None

        grouped_dist = round(result['dist'], 1) if result.get('Dist') else None

        if len(dist_grouped_results) == 0:
            dist_grouped_results[grouped_dist].append(result)
        else:
            closest_dist = data_helper.lowest_percent_diff_element(dist_grouped_results, grouped_dist)
            closest_percent_diff = data_helper.get_abs_percent_diff(grouped_dist, closest_dist)

            # If not significantly different, converge this distance to the closest
            if closest_percent_diff < dist_grouping_percent_diff:
                grouped_dist = closest_dist

        dist_grouped_results[grouped_dist].append(result)

    return dist_grouped_results
