import scipy.stats
from helpers import data_helper

def add_percentile_field(result_list):
    race_grouped_results = data_helper.group(result_list, 'race_id')
    
    for race_id in race_grouped_results:
        results_for_race = race_grouped_results[race_id]
        times_for_race = [get_time(result) for result in results_for_race if get_time(result)]
        for result in results_for_race:
            time = get_time(result)
            
            if time:
                result['percentile'] = str(round(100-scipy.stats.percentileofscore(times_for_race, time), 1))
            else:
                result['percentile'] = str(0.0)

def get_time(result):
    return result.get('net_time') or result.get('gun_time')