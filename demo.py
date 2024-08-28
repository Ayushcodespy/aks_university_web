
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="ayush7085",
    database="ayush"
)

cursor = mydb.cursor()
username = 'B2255R10106223'
password = 'ayush7085'
cursor.execute("Select * FROM STUDENTS WHERE STUDENT_ID = 'B2255R10106223'")
login = cursor.fetchone()
print(login)