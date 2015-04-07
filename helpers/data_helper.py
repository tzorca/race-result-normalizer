import datetime
import statistics

def get_blank_ratio(dicts, key_name):
    blank_count = 0
    for dictionary in dicts:
        if not key_name in dictionary:
            continue
        if dictionary[key_name] is None:
            blank_count += 1
        elif len(str(dictionary[key_name]).strip()) == 0:
            blank_count += 1

    return blank_count / float(len(dicts))


def cluster_list_of_dicts(list_dicts, key, max_cluster_count, min_difference):
    # Get differences between each dictionary[key] (and indexes)
    differences = get_list_of_dicts_differences(list_dicts, key)

    # Sort difference list by descending difference
    differences.sort(key=lambda tup: tup[1], reverse=True)

    # Remove differences below min_difference
    differences = [d for d in differences if d[1] >= min_difference]

    # Get top differences
    max_difference_count = max_cluster_count - 1
    saved_difference_count = min([len(differences), max_difference_count])
    top_differences = differences[0: saved_difference_count]
    
    # Get "split after" indexes sorted in descending order
    split_after_indexes = [d[0] + 1 for d in top_differences]
    split_after_indexes.sort(reverse=True)

    # Split into clusters
    clusters = []
    remaining_dicts = list_dicts[:]
    for split_after_index in split_after_indexes:
        clusters.append(remaining_dicts[split_after_index:])
        remaining_dicts = remaining_dicts[:split_after_index]
    if len(remaining_dicts):
        clusters.append(remaining_dicts)

    return clusters


def get_list_of_dicts_differences(list_dicts, key):
    differences = []
    for i, (dict_l, dict_r) in enumerate(zip(list_dicts, list_dicts[1:])):
        difference = dict_r.get(key) - dict_l.get(key)
        differences.append((i, difference))
        
    return differences


EPOCH = datetime.datetime(1970,1,1)
def get_timestamp(datetime_obj):
    return (datetime_obj - EPOCH).total_seconds()


def remove_datetime_outliers(datetime_population, sigmas):
    if len(datetime_population) < 3:
        return datetime_population
    
    timestamp_population = [get_timestamp(dt) for dt in datetime_population]
    
    mean_val = statistics.mean(timestamp_population)
    std_devs = statistics.pstdev(timestamp_population) * sigmas
             
    def not_outlier(x):
        if abs(x - mean_val) <= std_devs:
            return x
 
    return [dt for dt, ts in zip(datetime_population, timestamp_population) if not_outlier(ts)]


def split_into_sublists(the_list, sublist_size):
    return [the_list[x:x+sublist_size] for x in range(0, len(the_list), sublist_size)]
