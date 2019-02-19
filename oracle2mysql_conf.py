import getpass
import os
import sys

import cx_Oracle
import MySQLdb

oracle_host = input("Oracle hostname: ")
oracle_username = input("Oracle username: ")
oracle_service = input("Oracle service (For example: orcl): ")
oracle_password = getpass.getpass("Oracle password: ")

oracle = cx_Oracle.connect(oracle_username, oracle_password, "(DESCRIPTION = (ADDRESS_LIST = (ADDRESS = (PROTOCOL = TCP)(HOST = %s)(PORT = 1521))) (CONNECT_DATA = (SERVICE_NAME = %s)))" % (oracle_host,oracle_service))

mysql_db = input("\nMySQL database name: ")
mysql_host = input("MySQL hostname: ")
mysql_username = input("MySQL username: ")
mysql_password = getpass.getpass("MySQL password: ")

mysql = MySQLdb.connect(
    db=mysql_db,
    user=mysql_username,
    passwd=mysql_password,
    host=mysql_host,
    use_unicode=True,
    charset='utf8')

tables = (
    'probandoOracle1',
    'probandoOracle2',
)
