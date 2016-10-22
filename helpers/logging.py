log_entries = []


def log_error(filename, category, details):
    log_entries.append({
        'error': True,
        'filename': filename,
        'category': category,
        'details': details,
    })


def log_info(filename, category, details):
    log_entries.append({
        'error': False,
        'filename': filename,
        'category': category,
        'details': details,
    })
