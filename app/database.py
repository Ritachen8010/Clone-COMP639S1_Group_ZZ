import mysql.connector
import app.connect as connect

dbconn = None
connection = None

# While use cursor, please use cursor = getCoursor
def getCursor():
    global connection

    # Check if the existing connection is still valid
    if connection is None or not connection.is_connected():
        try:
            connection = mysql.connector.connect(user=connect.dbuser,
                                                 password=connect.dbpass,
                                                 host=connect.dbhost,
                                                 database=connect.dbname,
                                                 autocommit=True)
        except mysql.connector.Error as err:
            print("Error connecting to database: ", err)
            return None  # or raise an exception

    return connection.cursor(dictionary=True)


# While use connection, please use connection = getConnection
def getConnection():
    global connection
    # maske sure connection = None
    if connection is None:
        getCursor() 
    return connection