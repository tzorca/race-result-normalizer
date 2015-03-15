import pymysql
import re

def create_table(db_connection: pymysql.Connection, table_def):
    sql = "create table if not exists `%s` (" % (table_def["name"])

    column_def_strings = []
    for column_def in table_def["columns"]:
        column_def_strings.append("%s %s" % (column_def["name"], column_def["type"]))
    sql += ",".join(column_def_strings);

    sql += ");"
    
    try:
        cursor = db_connection.cursor()
        cursor.execute(sql)
    except Exception as e:
        print(sql)
        print(e)
    cursor.close()
    
def drop_table(db_connection: pymysql.Connection, table_name):
    cursor = db_connection.cursor()
    cursor.execute("drop table if exists `%s`" % (table_name)) 
    cursor.close()

            
def insert_rows(db_connection: pymysql.Connection, table_def, rows):
    column_renames = table_def["column_renames"]
    column_defs = table_def["columns"]
    
    for row in rows:
        column_names = []
        parameters = []
        placeholders = []
        
        for column_name in row:
            if (column_name in column_renames):
                column_name = column_renames[column_name]
            
            if (column_name not in column_defs):
                continue
                
            validate_identifier(column_name)
            
            column_names.append(column_name)
            parameters.append(row[column_name])
            placeholders.append("%s")
        
        column_names_string = "(" + ",".join(column_names) + ")"
        placeholders_string = "(" + ",".join(placeholders)  + ")"
        
        cursor = db_connection.cursor()
        cursor.execute("insert into " + table_def["name"] + " " + column_names_string + 
                       " values " + placeholders_string + ";", parameters)
    cursor.close()

            
IDENTIFIER_VALIDATOR = re.compile(r'^[0-9a-zA-Z_\$]+$');
def validate_identifier(name):
    if not IDENTIFIER_VALIDATOR.match(name):
        raise ValueError("%s is not a valid identifier." % name)
