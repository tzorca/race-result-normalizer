def rows_to_csv(rows, separator):
    field_indexes = {}
    out_buffer = []

    # Assign a unique index to each fieldName 
    for row in rows:
        for fieldName in row:
            if (fieldName not in field_indexes):
                field_indexes[fieldName] = len(field_indexes)

    # Append header to output
    header = [""] * len(field_indexes)
    for fieldName in field_indexes:
        index = field_indexes[fieldName]
        header[index] = fieldName
    out_buffer.append(separator.join(header))
    
    # Append data
    for row in rows:
        line = [""] * len(field_indexes)

        for fieldName in row:
            index = field_indexes[fieldName]
            line[index] = row[fieldName]

        out_buffer.append(separator.join(line))

    return '\n'.join(out_buffer)