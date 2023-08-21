import mysql.connector

# Replace these values with your database configuration
db_config = {
    "host": "192.168.0.188",
    "user": "mus_pi",
    "password": "21ftt1241",
    "database": "pi_test"
}

# Establish a connection to the database
connection = mysql.connector.connect(**db_config)

if connection.is_connected():
    cursor = connection.cursor()
    
    query = "SELECT * FROM user"
    cursor.execute(query)
    
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        
    cursor.close()

# Close the connection when you're done
connection.close()
