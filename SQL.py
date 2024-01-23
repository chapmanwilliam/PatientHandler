import sqlite3
from sqlite3 import OperationalError

def getConnection():
    connection = sqlite3.connect('patients.sqlite')
    return connection

def getCursor():
    connection = getConnection()
    connection.row_factory = sqlite3.Row
    cursor=connection.cursor()
    return cursor
def executeScriptsFromFile(filename, search=None):
    # Open and read the file as a single buffer
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()

    # all SQL commands (split on ';')
    sqlCommands = sqlFile.split(';')

    connection=getConnection()
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()


    # Execute every command from the input file
    for command in sqlCommands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            if search is None:
                result=cursor.execute(command)
            else:
                result = cursor.execute(command, search)
        except OperationalError as msg:
            print("Command skipped: ", msg)
            return None
    connection.commit()
    return result

def getLastRowInsertID(table_name):
    # Open and read the file as a single buffer


    # all SQL commands (split on ';')

    connection=getConnection()
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    command="SELECT max(rowid) FROM " + table_name
    cursor.execute(command)
    max_id = cursor.fetchone()[0]
    return max_id

def convert_into_binary(file_path):
  with open(file_path, 'rb') as file:
    binary = file.read()
  return binary

#print (executeScriptsFromFile('SQL/DeletePatient.sql',(3,)).fetchall())
#print (getLastRowInsertID("DOCTORS"))
