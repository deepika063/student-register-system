# student-register-system

PROJECT CONTENT
1.Backend (Flask API Layer)
Flask App Setup: Main application setup with app.py
API Endpoints:
POST /addstudent: Add a new student and generate a unique register number
GET /viewstudents: Fetch all student records
GET /filter: Retrieve students by department
GET /studentbyregno/<regno>: Retrieve a student by register number
PUT /updatestudentdetails/<id>: Update student information
DELETE /deletestudent/<regno>: Delete student by register number
Database Configuration:
Connection with MySQL using Flask-MySQLdb
Schema design with fields: id, name, department, joining_year, status, register_number
 2. Frontend (HTML, CSS, JS)
Pages:
index.html: Add student
filter.html: Filter students by department
update.html: Update student using register number
delete.html: Delete student after login
view.html: View all student records in tabular form
Styling:
Modern, responsive UI using custom CSS
Shared footer for consistent branding
Smooth animations and clean design
JavaScript:
Fetch API used for communicating with Flask backend
Dynamic DOM updates and form handling
 3. Authentication Layer
Simple admin login UI for delete operation
Placeholder logic for authentication
4. Utilities
Postman Collection:
API testing and documentation
Example requests and responses for each endpoint
Error Handling:
Graceful alerts for network and server errors
JSON-based error messages from backend

PROJECT CODE

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

KEY TECHNOLOGIES USED
  Frontend
     HTML5 – Markup language used to structure the pages.
     CSS3 – For styling and animations to create a visually appealing and responsive UI.
     JavaScript – For dynamic client-side interactions, API calls, and DOM manipulation.
  Backend
     Python – Core programming language used to build the server-side logic.
     Flask – Lightweight web framework used to create RESTful APIs and route handling.
  Database 
     MySQL – Relational database used to store student records with CRUD operations.
  API Tools 
    Flask-MySQLdb – A Flask extension used to interact with MySQL databases.
    Postman – API testing tool used for testing endpoints during development.
  Version Control / Collaboration
    Git & GitHub – Used for source code management and collaboration.

DESCRIPTION
    Automated Student Register Generation System is a backend-focused project that showcases the design and development of RESTful APIs for managing student records in an academic institution.
The project is built using Flask,a lightweight Python web framework,and follows REST principles to perform CRUD operations (Create, Read, Update, Delete) on student data stored in a MySQL database.The system automates the generation of unique register numbers based on the student's department and year of joining, ensuring consistency and uniqueness across entries.
A minimal yet modern frontend was added to demonstrate API consumption using HTML, CSS, and JavaScript, with responsive styling and intuitive UI components.
This project is a practical implementation of API development and integration with relational databases, and serves as a strong foundation for building scalable backend services in real-world educational software systems.

OUTPUT

![image](https://github.com/user-attachments/assets/a566e5f8-1e6e-485d-bebe-278c85084dfd)

![image](https://github.com/user-attachments/assets/0a87066b-0315-417e-a0e1-4211356d0ff8)

![image](https://github.com/user-attachments/assets/a8f3e304-281c-4950-9bfd-77b749f4da8a)

![image](https://github.com/user-attachments/assets/099a4a28-debe-46d3-8db2-d71773a165f5)

![image](https://github.com/user-attachments/assets/e60f3fc5-5822-431d-82d3-d60c59380158)

![image](https://github.com/user-attachments/assets/b4034ad9-8087-4b3a-a31a-9fa30510bd9f)

![image](https://github.com/user-attachments/assets/7d720393-9356-4774-93e1-0fd9cbb96b90)

![image](https://github.com/user-attachments/assets/8b45d8ea-b6f5-4682-8ddb-809b696bf7be)
 
FURTHER RESEARCH
The Automated Student Register Generation System provides a solid foundation for managing student data and generating register numbers using a RESTful API, there are multiple areas for further research and development to improve the functionality, scalability, and usability of the system:
1. Authentication & Authorization
•	Implement role-based authentication (e.g., admin, staff, viewer).
•	Use JWT (JSON Web Tokens) or OAuth 2.0 for secure API access.
•	Add session management and login/logout functionalities.
2. Data Validation and Security
•	Implement backend data validation using libraries like marshmallow or pydantic.
•	Use parameterized queries or ORM (e.g., SQLAlchemy) to prevent SQL injection.
•	Apply HTTPS for secure communication.
3. Register Number Customization
•	Enable dynamic register number formats based on institution-specific patterns.
•	Support for prefixes/suffixes based on batch, program, or college codes.
4. Database Optimization
•	Normalize the schema for scalability and better performance.
•	Add indexing for frequently searched fields (e.g., register_number, department).
•	Use stored procedures for complex operations.
5. Deployment & Hosting
•	Dockerize the application for consistent environment setup.
•	Deploy the app using cloud platforms like Heroku, Render, AWS, or GCP.
•	Set up CI/CD pipelines using GitHub Actions or GitLab CI.
6. Frontend Enhancements
•	Convert static HTML/CSS to dynamic UI using React.js or Vue.js.
•	Implement pagination, sorting, and searching capabilities in the data tables.
•	Improve accessibility (ARIA tags, keyboard navigation, contrast ratios).
7. Logging & Monitoring
•	Add logging using Python’s logging module or tools like Loguru.
•	Integrate monitoring tools like Prometheus or Grafana for API health.
8. PDF/Excel Reports
•	Add an endpoint to export student records as downloadable PDF or Excel files.
•	Include filters (e.g., department-wise report, year-wise report).
9. Multi-Institution Support
•	Extend the system to support multiple colleges or departments from different campuses.
•	Add tenant-based database design or dynamic schema switching.
10. Mobile App Integration
•	Build a mobile companion app using Flutter or React Native to allow administrators and students to view or manage data on the go.
