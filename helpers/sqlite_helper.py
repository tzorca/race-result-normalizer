import re


def create_table(db, table_def):
    column_defs = table_def["columns"]
    ext_table_def = table_def.get("ext_table_def")

    sql = "create table if not exists `%s` (" % (table_def["name"])

    column_def_strings = []
    for column_name in column_defs:
        column_def_strings.append("%s %s" % (column_name, column_defs[column_name]))
    sql += ",".join(column_def_strings)

    if ext_table_def:
        sql += "," + ext_table_def

    sql += ");"

    cursor = db.cursor()
    cursor.execute(sql)
    cursor.close()
    db.commit()


def drop_table(db, table_name):
    cursor = db.cursor()
    cursor.execute("drop table if exists `%s`" % table_name)
    cursor.close()
    db.commit()


def insert_row(db, table_def, row):
    return insert_rows(db, table_def, [row])


def insert_rows(db, table_def, rows):
    insert_id = None

    # Get a list of column names to be used
    if len(rows) == 0:
        print("No rows to insert for " + table_def["name"])
        return

    column_defs = table_def["columns"]

    first_row = rows[0]
    col_names = []
    for col_name in first_row:
        if col_name not in column_defs:
            continue
        if not validate_identifier(col_name):
            continue
        col_names.append(col_name)

    # Build first part of SQL string
    insert_sql_start = "insert or ignore into " + table_def["name"] + " (" + ",".join(col_names) + ") values "

    placeholders_string = "(" + ",".join(["?"] * len(col_names)) + ") "

    cursor = db.cursor()

    insert_sql = insert_sql_start + placeholders_string + ";"

    row_params_list = []
    row_params = []
    for row in rows:
        row_params = []
        for col_name in col_names:
            if col_name in row:
                row_params.append(row[col_name])
            else:
                row_params.append(None)
        row_params_list.append(row_params)

    try:
        if len(row_params_list) == 1:
            cursor.execute(insert_sql, row_params_list[0])
            insert_id = cursor.lastrowid
            print(insert_id)
        else:
            cursor.executemany(insert_sql, row_params_list)
    except Exception as e:
        print(e)
        print(row_params)
        print(insert_sql)

    db.commit()
    cursor.close()

    return insert_id


def run_commands(db, command_list):
    cursor = db.cursor()
    for command in command_list:
        cursor.execute(command)
    cursor.close()
    db.commit()


IDENTIFIER_VALIDATOR = re.compile(r'^[0-9a-zA-Z_\$]+$')


def validate_identifier(name):
    if not IDENTIFIER_VALIDATOR.match(name):
        raise ValueError("%s is not a valid identifier." % name)
    return True
