import mysql.connector
import app.connect as connect

dbconn = None
connection = None

# While use cursor, please use cursor = getCoursor
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


# While use connection, please use connection = getConnection
def getConnection():
    global connection
    # maske sure connection = None
    if connection is None:
        getCursor() 
    return connection