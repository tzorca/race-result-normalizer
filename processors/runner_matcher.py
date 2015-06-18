from collections import defaultdict
from helpers import data_helper
import datetime
import math


YEARS_BEFORE_SPLIT = 3
DUMMY_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)


def match_runners(all_results):
    runners = []
    runner_id = 1
    
    # Group all_results by name, then sex
    results_by_name_then_sex = defaultdict(lambda : defaultdict(list))
    for result in all_results:
        results_by_name_then_sex[result.get('runner_name')][result.get('sex')].append(result)
    
    # Loop through grouped results
    for name in results_by_name_then_sex:
        # Get results and sort by birthdate_lte
        specific_name_results = results_by_name_then_sex[name]
        specific_name_male_results = sorted(specific_name_results.get('M') or [], 
            key=sort_by_birthdate_lte_or_dummy)
        specific_name_female_results = sorted(specific_name_results.get('F') or [],
            key=sort_by_birthdate_lte_or_dummy)
        specific_name_blank_gender_results = sorted(specific_name_results.get('') or [],
            key=sort_by_birthdate_lte_or_dummy)
            
        # Try generating clusters for males + blanks; females
        male_and_blank_results = list(specific_name_male_results)
        male_and_blank_results.extend(specific_name_blank_gender_results)
        attempt_1 = {
            'M': cluster_results_by_birthdate_lte(male_and_blank_results),
            'F': cluster_results_by_birthdate_lte(specific_name_female_results)
        }
        
        # Try generating clusters for females + blanks; males 
        female_and_blank_results = list(specific_name_female_results)
        female_and_blank_results.extend(specific_name_blank_gender_results)
        attempt_2 = {
            'M': cluster_results_by_birthdate_lte(specific_name_male_results),
            'F': cluster_results_by_birthdate_lte(female_and_blank_results)
        }
        
        # Pick the attempt with the lowest number of clusters
        attempt_1_clusters = len(attempt_1['M']) + len(attempt_1['F'])
        attempt_2_clusters = len(attempt_2['M']) + len(attempt_2['F'])
        result_clusters_by_sex = attempt_1 if attempt_1_clusters < attempt_2_clusters else attempt_2

        # Create runners
        for sex in result_clusters_by_sex:
            result_clusters = result_clusters_by_sex[sex]
            for result_cluster in result_clusters:
                if len(result_cluster) == 0:
                    continue
                
                approximate_birthdate = approximate_birthdate_from_results(result_cluster)
                name = result_cluster[0]['runner_name']
                for result in result_cluster:
                    result['runner_id'] = runner_id
                    
                runners.append({
                    'id': runner_id, 'name': name, 'sex': sex,
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

        