import pymysql
import re
from helpers import data_helper

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

BATCH_INSERT_LIMIT = 500
def insert_rows(db_connection: pymysql.Connection, table_def, rows):
    column_defs = table_def["columns"]

    # Build column names string from column definitions
    column_names_string = "(" + ",".join([c for c in column_defs if validate_identifier(c)]) + ")"
    
    # Build first part of SQL string
    insert_sql_start = "insert into " + table_def["name"] + " " + column_names_string + " values "

    placeholders_string = ["(" + ",".join(["%s"]*len(column_defs))  + ") "]

    cursor = db_connection.cursor()
    batches = data_helper.split_into_sublists(rows, BATCH_INSERT_LIMIT)
    for batch in batches:
        
        # Get all parameters in batch
        parameters = []
        for row in batch:
            for column_name in column_defs:
                parameters.append(row.get(column_name))
        
        insert_sql = insert_sql_start + ",".join(placeholders_string * len(batch)) + ";"
        try:
            cursor.execute(insert_sql, parameters)
        except Exception as e:
            print(e)
            print(insert_sql)
            print(parameters)
        
    cursor.close()
    db_connection.commit()

            
IDENTIFIER_VALIDATOR = re.compile(r'^[0-9a-zA-Z_\$]+$');
def validate_identifier(name):
    if not IDENTIFIER_VALIDATOR.match(name):
        raise ValueError("%s is not a valid identifier." % name)
        return False
    return True
