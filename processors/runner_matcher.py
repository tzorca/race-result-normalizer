from collections import defaultdict
from helpers import data_helper
import datetime
import math


YEARS_BEFORE_SPLIT = 3
DUMMY_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)


def match_runners(all_results):
    runners = []
    runner_id = 0
    
    # Group all_results by name and sex
    results_by_name_and_sex = defaultdict( list )
    for result in all_results:
        results_by_name_and_sex[(result.get('runner_name'), result.get('sex'))].append(result)
    
    # Loop through grouped results
    for key in results_by_name_and_sex:
        current_results = results_by_name_and_sex[key]
        
        # Sort current_results by birthdate_lte
        current_results = sorted(current_results, key=sort_by_birthdate_lte_or_dummy)

        # Generate clusters from birthdate_lte       
        result_clusters = cluster_results_by_birthdate_lte(current_results)

        # Create runners
        name = key[0]
        sex = key[1]
        for result_cluster in result_clusters:
            result['runner_id'] = runner_id
            approximate_birthdate = approximate_birthdate_from_results(result_cluster)
                    
            runners.append({
                'id': runner_id, 
                'name': name, 
                'sex': sex,
                'approximate_birthdate': approximate_birthdate
            })
            runner_id += 1
    
    return runners


def cluster_results_by_birthdate_lte(results):
    # Default to a single cluster
    result_clusters = [results]
    
    # Get all not None birthdate_lte in current_results
    birthdate_lte_list = [r['birthdate_lte'] for r in results if r.get('birthdate_lte')]
    
    # If there were enough birthdate_lte elements in the list
    if birthdate_lte_list and len(birthdate_lte_list) > 1:
        # Get range of birthdate_lte
        birthdate_year_range = (max(birthdate_lte_list) - min(birthdate_lte_list)).days / (365.25)
    
        # Cluster into multiple runners based on YEARS_BEFORE_SPLIT
        max_clusters = math.ceil(birthdate_year_range / float(YEARS_BEFORE_SPLIT))
        if max_clusters > 1:
            min_difference = datetime.timedelta(days=365.25*YEARS_BEFORE_SPLIT)
            result_clusters = data_helper.cluster_list_of_dicts(results, 'birthdate_lte', max_clusters, min_difference)

    return result_clusters


def approximate_birthdate_from_results(results):
    birthdate_lte_list = []
    approximate_birthdate = None
    for result in results:
        if result.get('birthdate_lte'):
            birthdate_lte_list.append(result['birthdate_lte'])
            
    if (len(birthdate_lte_list)):
        birthdate_lte_list = data_helper.remove_datetime_outliers(birthdate_lte_list, 2)
        approximate_birthdate = min(birthdate_lte_list)
    
    return approximate_birthdate


def sort_by_birthdate_lte_or_dummy(result):
    return result.get('birthdate_lte') or DUMMY_DATE

        