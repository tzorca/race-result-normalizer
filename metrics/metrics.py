from collections import defaultdict

error_file_details = defaultdict(list)

def add_error_file(filename, reason):
    error_file_details[reason].append(filename)

def print_error_files():
    for reason in error_file_details:
        files = error_file_details[reason]
        print("%s : %d files (%s)" % (reason, len(files), str(files)))
