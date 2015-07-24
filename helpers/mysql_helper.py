import pymysql
import re
from helpers import data_helper
import time

def create_table(db_connection: pymysql.Connection, table_def):
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
    
    cursor = db_connection.cursor()
    cursor.execute(sql)
    cursor.close()
    db_connection.commit()
    
    
def drop_table(db_connection: pymysql.Connection, table_name):
    cursor = db_connection.cursor()
    cursor.execute("drop table if exists `%s`" % (table_name)) 
    cursor.close()
    db_connection.commit()


def insert_row(db_connection: pymysql.Connection, table_def, row):
    column_defs = table_def["columns"]
    
    # Build column names string from column definitions
    column_names_string = "(" + ",".join([c for c in column_defs if validate_identifier(c)]) + ")"
    
    # Build first part of SQL string
    insert_sql_start = "insert ignore into " + table_def["name"] + " " + column_names_string + " values "
    
    
    placeholders_string = ["(" + ",".join(["%s"]*len(column_defs))  + ") "]
    
    cursor = db_connection.cursor()

    parameters = []
    for column_name in column_defs:
        field_value = row.get(column_name)
        if type(field_value) is time.struct_time:
            field_value = data_helper.get_time_str(field_value)
        parameters.append(field_value)
        insert_sql = insert_sql_start + ",".join(placeholders_string) + ";"
        
    try:
        cursor.execute(insert_sql, parameters)
    except Exception as e:
        print(e)
        print(insert_sql)
        print(row)
    
    last_id = cursor.lastrowid
    
    cursor.close()
    db_connection.commit()
    
    return last_id


BATCH_INSERT_LIMIT = 500
def insert_rows(db_connection: pymysql.Connection, table_def, rows):
    column_defs = table_def["columns"]

    # Build column names string from column definitions
    column_names_string = "(" + ",".join([c for c in column_defs if validate_identifier(c)]) + ")"
    
    # Build first part of SQL string
    insert_sql_start = "insert ignore into " + table_def["name"] + " " + column_names_string + " values "

    placeholders_string = ["(" + ",".join(["%s"]*len(column_defs))  + ") "]

    cursor = db_connection.cursor()
    batches = data_helper.split_into_sublists(rows, BATCH_INSERT_LIMIT)
    for batch in batches:
        
        # Get all parameters in batch
        parameters = []
        for row in batch:
            for column_name in column_defs:
                field_value = row.get(column_name)
                if type(field_value) is time.struct_time:
                    field_value = data_helper.get_time_str(field_value)
                parameters.append(field_value)
        
        insert_sql = insert_sql_start + ",".join(placeholders_string * len(batch)) + ";"
        try:
            cursor.execute(insert_sql, parameters)
        except Exception as e:
            print(e)
            print(insert_sql)
            print(batch)
        
    cursor.close()
    db_connection.commit()


def run_commands(db_connection: pymysql.Connection, command_list):
    cursor = db_connection.cursor()
    for command in command_list:
        cursor.execute(command) 
    cursor.close()
    db_connection.commit()
           
            
IDENTIFIER_VALIDATOR = re.compile(r'^[0-9a-zA-Z_\$]+$');
def validate_identifier(name):
    if not IDENTIFIER_VALIDATOR.match(name):
        raise ValueError("%s is not a valid identifier." % name)
        return False
    return True
