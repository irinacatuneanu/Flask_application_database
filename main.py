from flask import Flask
from flask import redirect, url_for, request, render_template, send_file
from io import BytesIO
from flask_wtf.file import FileField
from wtforms import SubmitField
from flask_wtf import Form
import sqlite3
import time
from datetime import date
import hashlib

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
DB = 'Files2.db'

@app.route('/', methods=["GET", "POST"])
def index():
    files = query_filename()
    form = UploadForm()
    if request.method == "POST":
        if form.validate_on_submit():
            file_name = form.file.data
            database(name=file_name.filename, data=file_name.read() )
            return render_template("home.html", form=form, files=files)
    return render_template("home.html", form=form, files=files)

@app.route("/view")
def view():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from my_table")
    rows = cur.fetchall()
    return render_template("view.html",rows = rows)

@app.route('/download', methods=["GET"])
def download():
    conn= sqlite3.connect(DB)
    cursor = conn.cursor()
    print("IN DATABASE FUNCTION ")
    c = cursor.execute(""" SELECT * FROM  my_table WHERE rowid = ?""",(request.args.get('id')))
    for x in c.fetchall():
        name_v=x[0]
        data_v=x[1]
        break
    conn.commit()
    cursor.close()
    conn.close()
    return send_file(BytesIO(data_v), attachment_filename=name_v, as_attachment=True)


class UploadForm(Form):
    file = FileField()
    submit = SubmitField("submit")
    download = SubmitField("download")

def database(name, data):
    conn= sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO my_table (name, data,timestamp ) VALUES (?,?,?) """,(name,data,time.time()))
    conn.commit()
    cursor.close()
    conn.close()

def query():
    conn= sqlite3.connect(DB)
    cursor = conn.cursor()
    print("IN DATABASE FUNCTION ")
    c = cursor.execute(""" SELECT * FROM  my_table """)
    for x in c.fetchall():
        name_v=x[0]
        data_v=x[1]
        break
    conn.commit()
    cursor.close()
    conn.close()
    return send_file(BytesIO(data_v), attachment_filename='flask.pdf', as_attachment=True)

def create_table(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS my_table (name TEXT, data BLOB, timestamp INTEGER ) """)

def query_filename():
    files = []
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    print("IN DATABASE FUNCTION ")
    create_table(cursor)
    c = cursor.execute(""" SELECT *, rowid FROM  my_table """)
    for x in c.fetchall():
        files.append({'name':x[0],'size':len(x[1]),'timestamp':date.fromtimestamp(x[2]).isoformat(),'id': x[3], 'hash':hashlib.sha256(x[1]).hexdigest()})
    conn.close()
    return files

@app.route('/delete')
def delete():
    return render_template('delete.html')


@app.route('/delete_file',methods=['POST'])
def delete_file():
    id = request.form["id"]
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM my_table WHERE rowid = ?",id)
    msg = "record successfully deleted"
    return render_template('delete_file.html',msg=msg)

if __name__ == "__main__":
    app.run(port=9000,debug=True)