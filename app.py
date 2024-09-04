from flask import Flask, Response, abort, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
import mysql.connector
import random
import razorpay
from datetime import datetime

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

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=("rzp_test_dqRgrGCBhYV2Ul", "OihbG5dQPxWMYXDjnAmMNjd9"))



mydb = mysql.connector.connect(
    host="mysql-dkns.railway.internal",
    user="root",
    passwd="xvVvFlzkwAgJJUyFWvKMGnRqIzsFnbzX",
    database="railway",
    port=15530
)

cursor = mydb.cursor()


@app.route('/')
def home():
    if 'user' in session:
        cursor.execute("Select * FROM STUDENTS WHERE STUDENT_ID = %s", (session['user'],))
        result = cursor.fetchone()
        return render_template("index.html", active_page='home', details=result)

    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        username = request.form['user_id']
        password = request.form['passwd']
        cursor.execute("Select Student_ID, Password from login where Student_ID = %s AND Password = %s",
                       (username, password))
        _login = cursor.fetchone()
        if _login:
            session['user'] = _login[0]
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error='Incorrect login details!')
    return render_template('login.html')


@app.route("/profile")
def profile():
    if 'user' in session:
        # cursor.execute("Select * FROM STUDENTS WHERE STUDENT_ID = %s", (session['user'],))
        cursor.execute('''SELECT Students.*, Departments.Department_Name
                       FROM Students
                       JOIN Departments ON Students.Dept_ID = Departments.Department_ID
                        WHERE STUDENT_ID = %s''', (session['user'],))
        result = cursor.fetchone()
        return render_template("profile_page.html", active_page='profile', details=result)

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


@app.route('/fees')
def fees():
    # cursor.execute("Select * FROM STUDENTS WHERE STUDENT_ID = %s", (session['user'],))
    cursor.execute('''Select 
                    Students.*, Departments.Department_Name, Fee_Details.*
                    FROM Students
                    JOIN Departments ON Students.Dept_ID = Departments.Department_ID
                    JOIN Fee_Details ON Students.Student_ID = Fee_Details.Student_ID
                    WHERE Students.STUDENT_ID = %s ''', (session['user'],))
    result = cursor.fetchone()

    cursor.fetchall()

    cursor.execute('Select Deposit from Fee_Details where Student_ID = %s', (session['user'],))
    _fees = cursor.fetchall()
    paid = 0
    for i in _fees:
        # print(i)
        paid += i[0]

    if paid < 60000:
        amount_to_be_paid = 60000 - paid
        status = 'NOT CLEAR'

    else:
        status = 'CLEAR'
        amount_to_be_paid = 0.00
    # print(amount_to_be_paid)
    return render_template("fee_page.html", result=result, fees=amount_to_be_paid, status=status)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        amount_paid = request.form['selected_fees']
        return render_template('payment.html', pay = float(amount_paid))
    

@app.route('/payment-success', methods=['POST'])
def payment_success():
    if request.method == 'POST':
        # Get the payment_id from the request
        payment_id = request.json.get('payment_id')

        try:
            # Fetch the payment details from Razorpay
            payment = razorpay_client.payment.fetch(payment_id)

            # Extract the amount (it is in the smallest currency unit, e.g., paise for INR)
            amount = payment['amount'] / 100  # Convert to actual currency unit (e.g., from paise to INR)

            # You can also extract other details like:
            currency = payment['currency']
            status = payment['status']

            # Now, you can store these details in your database, update the payment status, etc.
            cursor.execute("INSERT INTO Fee_Details values(%s, %s, %s, %s)", (session['user'], amount, datetime.now().date(), 5,))
            mydb.commit()

            # Redirect to the fees page
            return redirect(url_for('fees'))

        except razorpay.errors.BadRequestError as e:
            # Handle error if payment_id is invalid or Razorpay API call fails
            return f"An error occurred: {str(e)}", 400




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
        student_code = request.form['student_code']
        cursor.execute("Select email from login where student_id = %s", (student_code,))
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
            return "Wrong otp"


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
