import sqlite3
import re
from helpers import data_helper
import time

def create_table(db, table_def):
    column_defs = table_def["columns"]
    ext_table_def = table_def.get("ext_table_def")
    
    sql = "create table if not exists `%s` (" % (table_def["name"])

    column_def_strings = []
    for column_name in column_defs:
        column_def_strings.append("%s %s" % (column_name, column_defs[column_name]))
    sql += ",".join(column_def_strings);
    
    if ext_table_def:
        sql += "," + ext_table_def 

    sql += ");"
    
    cursor = db.cursor()
    cursor.execute(sql)
    cursor.close()
    db.commit()
    
    
def drop_table(db, table_name):
    cursor = db.cursor()
    cursor.execute("drop table if exists `%s`" % (table_name)) 
    cursor.close()
    db.commit()


def insert_row(db, table_def, row):
    return insert_rows(db, table_def, [row])

def insert_rows(db, table_def, rows):
    insert_id = None

    column_defs = table_def["columns"]

    # Get a list of column names to be used
    first_row = rows[0];
    col_names = []
    for col_name in first_row:
        if not col_name in column_defs:
            continue
        if not validate_identifier(col_name):
            continue
        col_names.append(col_name)

    # Build first part of SQL string
    insert_sql_start = "insert or ignore into " + table_def["name"] + " (" + ",".join(col_names) + ") values "

    placeholders_string = "(" + ",".join(["?"]*len(col_names)) + ") "

    cursor = db.cursor()

    insert_sql = insert_sql_start + placeholders_string + ";"

    list_rows = []
    for row in rows:
        list_row = []
        for col_name in col_names:
            if col_name in row:
                list_row.append(row[col_name])
            else:
                list_row.append(None)
        list_rows.append(list_row)

    try:
        if len(list_rows) == 1:
            cursor.execute(insert_sql, list_rows[0])
            insert_id = cursor.lastrowid
            print(insert_id)
        else:
            cursor.executemany(insert_sql, list_rows)
    except Exception as e:
        print(e)
        print(list_row)
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
           
            
IDENTIFIER_VALIDATOR = re.compile(r'^[0-9a-zA-Z_\$]+$');
def validate_identifier(name):
    if not IDENTIFIER_VALIDATOR.match(name):
        raise ValueError("%s is not a valid identifier." % name)
        return False
    return True
