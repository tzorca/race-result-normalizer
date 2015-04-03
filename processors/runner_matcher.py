from collections import defaultdict
from helpers import data_helper
import datetime

YEARS_BEFORE_SPLIT = 3

def match_runners(all_results):
    runners = []
    runner_id = 0
    
    # Group all_results by name and sex
    results_by_name_and_sex = defaultdict( list )
    for result in all_results:
        name = result.get('runner_name')
        sex = result.get('sex')
        results_by_name_and_sex[(name, sex)].append(result)
    
    # Loop through grouped results
    for key in results_by_name_and_sex:
        current_results = results_by_name_and_sex[key]
        
        name = key[0]
        sex = key[1]
        
        # Default to a single cluster
        result_clusters = [current_results]
        
        # Sort current_results by birthdate_lte
        current_results = sorted(current_results, key=sort_by_birthdate_lte_or_dummy)
        
        # Get all not None birthdate_lte in current_results
        birthdate_lte_list = [r['birthdate_lte'] for r in current_results if r.get('birthdate_lte')]
        
        # If there were enough birthdate_lte elements in the list
        if birthdate_lte_list and len(birthdate_lte_list) > 1:
            # Get range of birthdate_lte
            birthdate_year_range = (max(birthdate_lte_list) - min(birthdate_lte_list)).days / (365.25)
        
            # Cluster into multiple runners based on YEARS_BEFORE_SPLIT
            max_clusters = round(birthdate_year_range / YEARS_BEFORE_SPLIT)
            if max_clusters > 1:
                min_difference = datetime.timedelta(days=365.25*YEARS_BEFORE_SPLIT)
                result_clusters = data_helper.cluster_list_of_dicts(current_results, 'birthdate_lte', max_clusters, min_difference)

        # Create runners
        for result_cluster in result_clusters:
            birthdate_lte_list = []
            for result in result_cluster:
                if result.get('birthdate_lte'):
                    birthdate_lte_list.append(result['birthdate_lte'].strftime("%Y-%m-%d"))
                result['runner_id'] = runner_id
                
            runners.append({
                'id': runner_id, 
                'name': name, 
                'sex': sex,
                'birthdate_lte_list': str(birthdate_lte_list)
            })
            runner_id += 1
    
    return runners
        
DUMMY_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)
def sort_by_birthdate_lte_or_dummy(result):
    return result.get('birthdate_lte') or DUMMY_DATE

        