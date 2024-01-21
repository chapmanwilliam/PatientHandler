import sqlite3
from sqlite3 import OperationalError

def getConnection():
    connection = sqlite3.connect('patients.sqlite')
    return connection

def getCursor():
    connection = getConnection()
    cursor=connection.cursor()
    return cursor
def executeScriptsFromFile(filename, search=""):
    # Open and read the file as a single buffer
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    cursor=getCursor()

    # Execute every command from the input file
    for command in sqlCommands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            result=cursor.execute(command, (search,))
        except OperationalError as msg:
            print("Command skipped: ", msg)
    return result

print (executeScriptsFromFile('SQL/List Patients Containing.sql').fetchall())

