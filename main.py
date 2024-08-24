from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "super-secret-key"

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
    if 'user' in session :
        cursor.execute("Select * FROM STUDENTS WHERE STUDENT_ID = %s", (session['user'],))
        result = cursor.fetchone()
        return render_template("profile_page.html", active_page='home', details = result)
    
    else:
        return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'user' in session : 
        return redirect(url_for('home'))

    if request.method == "POST":
        username = request.form['user_id']
        password = request.form['passwd']
        login = cursor.execute("Select Student_ID, Password from login where Student_ID = %s AND Password = %s", (username, password))
        login = cursor.fetchone()
        if login :
            session['user'] = login[0]
            return render_template('index.html')
        else:
            return render_template("login.html", error='Incorrect login details!')
    return render_template('login.html')


@app.route("/profile")
def profile():
    if 'user' in session :
        cursor.execute("Select * FROM STUDENTS WHERE STUDENT_ID = %s", (session['user'],))
        result = cursor.fetchone()
        return render_template("profile_page.html", active_page='profile', details = result)
    
    else:
        return redirect(url_for('login'))

@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
