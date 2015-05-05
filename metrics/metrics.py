from collections import defaultdict

grouped_errors = defaultdict(list)

def add_error(specific_info, error_class):
    grouped_errors[error_class].append(specific_info)

def print_errors():
    for error_class in grouped_errors:
        specific_info = grouped_errors[error_class]
        print("%s : %d specific_info (%s)" % (error_class, len(specific_info), str(specific_info)))
