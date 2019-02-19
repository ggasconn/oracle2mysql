# Oracle2MySQL
This is my fork for the helpful project that *codeforkjeff* did.
https://github.com/codeforkjeff/oracle2mysql

## Changes
Sorted from most important to less significant
- Migration from Python 2 to Python 3
- Added function migrate_users
- Ask for the MySQL data and Oracle service name.
- Handle a few errors with exceptions
- Added a few prints for a more verbose execution

## Requirements
```
cx_oracle
MySQLdb
os
sys
getpass
```
- cx_Oracle can be installed via pip and the documentation is here: https://oracle.github.io/python-cx_Oracle/
- MySQLdb could be substituted with any fork or compatible connector. I used mysqlclient, also available through pip and the documentation can be found here: https://pypi.org/project/mysqlclient/

## Use
```
python3 oracle2mysql.py oracle2mysql_conf
```
Executed without parameters returns the help

Hope you find it helpful and big thanks another time to *codeforkjeff* for his work!
