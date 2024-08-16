from flask import Flask, render_template

app = Flask(__name__)

import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="ayush7085",
    database="ayush"
)

cursor = mydb.cursor()
cursor.execute("SELECT * FROM BATCH2022")

result = cursor.fetchall()

@app.route('/')
def home():
    return render_template("login.html")


@app.route("/data")
def hello_world():
    return render_template("index.html", results=result)


if __name__ == "__main__":
    app.run(debug=True)
