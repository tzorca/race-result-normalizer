
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
