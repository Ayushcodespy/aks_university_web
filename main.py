from flask import Flask, Response, abort, g, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
import mysql.connector
import random


app = Flask(__name__)
app.secret_key = "super-secret-key"

# mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'patelayush.satna@gmail.com'
app.config['MAIL_PASSWORD'] = 'jlyw stso gslm vbey'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
# ------------------------------------------------------------------


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
            return redirect(url_for('home'))
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
    
@app.route('/image/<student_id>')
def get_image(student_id):
    cursor.execute("SELECT Image FROM STUDENTS WHERE STUDENT_ID = %s", (student_id,))
    image_data = cursor.fetchone()[0]

    if image_data:
        return Response(image_data, mimetype='image/jpeg')
    else:
        abort(404)

@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))


@app.route("/forget_pwd")
def forget_pwd():
    return render_template("forget_pwd.html")

@app.route("/send_otp", methods=['GET', 'POST'])
def send_otp():
    if request.method == 'POST':
        student_code =request.form['student_code']
        cursor.execute("Select email from login where student_id = %s",(student_code,))
        email = cursor.fetchone()
        email = email[0]
        if email is not None:
            session['id'] = student_code
        otp = random.randint(100000, 999999)
        session['otp'] = otp
        msg_to_user = Message(f'your otp is {otp}', sender='codestech01@gmail.com', recipients=[email])
        msg_to_user.body = "your otp is " + str(otp) 
        mail.send(msg_to_user)

        return render_template('otp_page.html')
    
@app.route("/verify_otp", methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = int(request.form['otp'])
        generated_otp = session.get('otp')
        if otp == generated_otp:
            return render_template("change_pwd.html")
        else:
            session.pop('id')
            return ("Wrong otp")


@app.route("/update_pwd", methods=['GET', 'POST'])
def update_pwd():
    if request.method == 'POST':
        new_pwd = request.form['new_password']
        conf_pwd = request.form['confirm_password']
        if new_pwd == conf_pwd:
            student_id = session.get('id')
            cursor.execute("UPDATE login SET Password = %s WHERE Student_ID = %s", (new_pwd, student_id))
            mydb.commit()
            session.pop('id')
            session.pop('otp')
            return redirect(url_for('login'))
        else:
            return "Passwords do not match."
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
