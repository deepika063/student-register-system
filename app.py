from flask import Flask,request,jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt,get_jwt_identity
from flask_cors import CORS
from datetime import datetime,timedelta
app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY']="vignan123"     #configure
jwt=JWTManager(app)
bcrypt=Bcrypt(app)
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']="root"
app.config['MYSQL_DB']="registerstudents"
app.config['MYSQL_HOST']="localhost"
mysql=MySQL(app)


@app.route("/addstudent",methods=["POST"])
def addstudent():
    data = request.json
    name = data['name']
    department = data['department']
    joining_year = int(data['joining_year'])
    status = "pending"
    # Convert joining year to 2-digit format like '23'
    year_suffix = str(joining_year)[-2:]
    prefix = f"2k{year_suffix}"
    # Department short codes (in uppercase)
    department_codes ={
        "Computer Science": "CSE",
        "Electronics": "ECE",
        "Mechanical": "MEC",
        "Electrical": "EEE"
    }
    dept_code=department_codes.get(department, "gen")  # default to 'gen'
    cur=mysql.connection.cursor()
    # Count students in the same department and year
    cur.execute("SELECT COUNT(*) FROM table1 WHERE department=%s AND joining_year=%s",(department, joining_year))
    count=cur.fetchone()[0] + 1  # increment for new student
    # Format sequence number to 3 digits
    seq=str(count).zfill(3)
    # Combine to create register number
    register_number=f"{prefix}{dept_code}{seq}"
    # Insert student record
    cur.execute(
        "INSERT INTO table1 (name, department, joining_year, status, register_number) VALUES (%s, %s, %s, %s, %s)",
        (name, department, joining_year, status, register_number)
    )
    mysql.connection.commit()
    return jsonify({"Message": "Student added successfully", "Register Number": register_number})


@app.route("/viewstudents", methods=["GET"])
def viewstudents():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, department, joining_year, status, register_number FROM table1")
    rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    results = [dict(zip(col_names, row)) for row in rows]
    return jsonify(results)

@app.route("/particularstudentdetails/<register_number>", methods=["GET"])
def particularstudentdetails(register_number):
    cur = mysql.connection.cursor()
    cur.execute("SELECT name, department, joining_year, status, register_number FROM table1 WHERE register_number=%s", (register_number,))
    row = cur.fetchone()
    if row:
        col_names = [desc[0] for desc in cur.description]
        result = dict(zip(col_names, row))
        return jsonify(result)
    return jsonify({"Error": "NO RECORD FOUND"})


@app.route("/updatestudentdetails/<int:id>", methods=["PUT"])
def updatestudentdetails(id):
    cur = mysql.connection.cursor()
    data = request.json
    name = data['name']
    department = data['department']
    joining_year = int(data['joining_year'])
    cur.execute("UPDATE table1 SET name=%s, department=%s, joining_year=%s WHERE id=%s",
                (name, department, joining_year, id))
    mysql.connection.commit()
    rowcount = cur.rowcount
    if rowcount == 0:
        return jsonify({"Error": "Record not found to modify"})
    return jsonify({"Message": "Data Updated successfully!", "id": id})


@app.route("/deletestudent/<register_number>", methods=["DELETE"])
def deletestudent(register_number):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM table1 WHERE register_number = %s", (register_number,))
    mysql.connection.commit()
    rowcount = cur.rowcount
    if rowcount == 0:
        return jsonify({"Error": "Record not found to delete"})
    return jsonify({"Message": "Record deleted successfully", "register_number": register_number})


@app.route("/filter", methods=["GET"])
def filter():
    department = request.args.get("department")
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, department, joining_year, status, register_number FROM table1 WHERE department = %s", (department,))
    rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    results = [dict(zip(col_names, row)) for row in rows]
    return jsonify(results)



@app.route("/stafflogin",methods=["POST"])
def stafflogin():
    data=request.json
    username=data['username']
    password=data['password']
    if not username or not password:
        return jsonify({"Error":"Missing credentials"})
    if username=="vignan" and password=="vignan123":
        return jsonify({"message":"Login success"})
    else:
        return jsonify({"message":"Login failed"})


#this is for a particular students according to their register number

@app.route("/studentbyregno/<string:regno>", methods=["GET"])
def studentbyregno(regno):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, department, joining_year FROM table1 WHERE register_number=%s", (regno,))
    row = cur.fetchone()
    if row:
        return jsonify({
            "id": row[0],
            "name": row[1],
            "department": row[2],
            "joining_year": row[3]
        })
    return jsonify({"Error": "Student with this Register Number not found"})





if __name__=="__main__":
    app.run(debug=True)
