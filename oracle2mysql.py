import os
import sys
import cx_Oracle
import MySQLdb

from MySQLdb import ProgrammingError, OperationalError

# need to set this, or Oracle won't retrieve utf8 chars properly
os.environ["NLS_LANG"]='AMERICAN_AMERICA.AL32UTF8'

def get_table_metadata(cursor):
    table_metadata = []
    # "The description is a list of 7-item tuples where each tuple
    # consists of a column name, column type, display size, internal size,
    # precision, scale and whether null is possible."
    for column in cursor.description:
        table_metadata.append({
            'name' : column[0],
            'type' : column[1],
            'display_size' : column[2],
            'internal_size' : column[3],
            'precision' : column[4],
            'scale' : column[5],
            'nullable' : column[6],
        })
    return table_metadata


def create_table(mysql, table, table_metadata):
    sql = "CREATE TABLE %s (" % (table,)
    column_definitions = []

    for column in table_metadata:
        # 'LINES' is a MySQL reserved word
        column_name = column['name']
        if column_name == "LINES":
            column_name = "NUM_LINES"

        if column['type'] == cx_Oracle.NUMBER:
            column_type = "DECIMAL(%s, %s)" % (column['precision'], column['scale'])
        elif column['type'] == cx_Oracle.STRING:
            if column['internal_size'] > 256:
                column_type = "TEXT"
            else:
                column_type = "VARCHAR(%s)" % (column['internal_size'],)
        elif column['type'] == cx_Oracle.DATETIME:
            column_type = "DATETIME"
        elif column['type'] == cx_Oracle.FIXED_CHAR:
            column_type = "CHAR(%s)" % (column['internal_size'],)
        else:
            raise Exception("No mapping for column type %s" % (column['type'],))

        if column['nullable'] == 1:
            nullable = "null"
        else:
            nullable = "not null"

        column_definitions.append("%s %s %s" % (column_name, column_type, nullable))

    sql += ",".join(column_definitions)

    sql += ") DEFAULT CHARACTER SET = utf8;"

    #print (sql)
    cursor = mysql.cursor()

    try:
        cursor.execute(sql)
    except ProgrammingError as e:
        print ("Could not create table: %s\nERROR: %s" % (table, e))

def migrate_data(oracle, mysql, table):
    oracle_cursor = oracle.cursor()
    mysql_cursor = mysql.cursor()

    # cursor.rowcount is supposed to contain # of records in query but
    # that doesn't seem to work for oracle, so we do SELECT count(*)
    # instead.
    sql = "SELECT count(*) FROM %s" % (table,)
    oracle_cursor.execute(sql)

    total_rows = oracle_cursor.fetchone()[0]

    oracle_cursor.execute("SELECT * FROM %s" % (table,))

    table_metadata = get_table_metadata(oracle_cursor)

    create_table(mysql, table, table_metadata)

    for x in range(total_rows):
        # TODO: should probably use fetchmany() and transactions to speed things up
        row = oracle_cursor.fetchone()

        column_names = []
        column_values = []
        index = 0
        for column in table_metadata:
            if column['name'] == 'LINES':
                column_names.append('NUM_LINES')
            else:
                column_names.append(column['name'])
            column_values.append(row[index])
            index += 1

        question_marks = ",".join(["%s" for i in range(len(column_names))])
        sql_insert = "INSERT INTO %s (%s) VALUES (%s)" % \
                     (table, ",".join(column_names), question_marks)

        mysql_cursor.execute(sql_insert, column_values)

def migrate_users(oracle, mysql):
    oracle_cursor = oracle.cursor()
    mysql_cursor = mysql.cursor()

    getUsersNumber = "SELECT count(*) FROM dba_users WHERE account_status = 'OPEN'"
    oracle_cursor.execute(getUsersNumber)

    total_rows = oracle_cursor.fetchone()[0]

    getUsersName = "SELECT username FROM dba_users WHERE account_status = 'OPEN'"
    oracle_cursor.execute(getUsersName)

    for x in range(total_rows):
        row = oracle_cursor.fetchone()
        username = row[0]
        createUser = "CREATE USER %s" % (username,)
        try:
            print("Creating user %s..." % (username,))
            mysql_cursor.execute(createUser)
        except OperationalError as e:
            print("\nERROR: %s\nMaybe the user already exists" % (e,))



def migrate(oracle, mysql, tables):
    #Migrate users with OPEN status
    migrate_users(oracle, mysql)

    for table in tables:
        print ("\nCreating table %s..." % (table,))
        migrate_data(oracle, mysql, table)
        print("Table %s migrated successfully....OK" % (table,))


if __name__=="__main__":
    if len(sys.argv) < 2:
        print ("""Usage: oracle2mysql.py CONF_MODULE_NAME

where CONFIG_MODULE is the name of a python module that defines 3 variables:
  oracle = a cx_Oracle connection object instance, to use for source
  mysql  = a MySQLdb connection object instance, to use for target
  tables = an iterable of string table names to migrate

Example:

# python oracle2mysql.py oracle2mysql_conf

""")
        sys.exit(0)

    conf_module_name = sys.argv[1]
    try:
        conf_module = __import__(conf_module_name)
    except ImportError as e:
        print ("""ERROR: Could not find config module: %s
                   Check if you wrote the module name ending with '.py'""" % (conf_module_name,))
        sys.exit(1)

    try:
        oracle = conf_module.oracle
        mysql = conf_module.mysql
        tables = tuple()
        tables = tables + conf_module.tables
    except AttributeError as e:
        print (e)
        sys.exit(1)

    migrate(oracle, mysql, tables)
