import mysql.connector

# Replace these values with your database configuration
db_config = {
    "host": "192.168.0.188",
    "user": "mus_pi",
    "password": "21ftt1241",
    "database": "db_test"
}

# Establish a connection to the database
connection = mysql.connector.connect(**db_config)
lockernum = "MG1"
otp = 1234

if connection.is_connected():
    cursor = connection.cursor()
    
    query = """
        SELECT r.rent_id, l.locker_number
        FROM rentdetail r
        INNER JOIN locker l ON r.locker_id = l.locker_id
        WHERE l.locker_number = %s AND l.locker_otp = %s
        """
    cursor.execute(query, (lockernum, otp))

    
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        
    cursor.close()

# Close the connection when you're done
connection.close()
