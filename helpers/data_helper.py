
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
