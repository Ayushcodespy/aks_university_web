from flask import Flask, render_template, request

app = Flask(__name__)

import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="ayush7085",
    database="ayush"
)

cursor = mydb.cursor()

@app.route('/')
def home():
    return render_template("login.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['user_id']
        password = request.form['passwd']
        login = cursor.execute(f"Select Student_ID, Password from login where Student_ID = '{username}' AND Password = '{password}'")
        login = cursor.fetchone()
        if (username == login[0] and password == login[1]):
            students = cursor.execute(f"Select Students.* from Students, Login where Students.Student_ID = '{username}' and Students.Student_ID = Login.Student_ID")
            students = cursor.fetchall()
            return render_template('index.html', student=students)
        else:
            return render_template("login.html", error='Incorrect login details!')
        


if __name__ == "__main__":
    app.run(debug=True)
