from flask import Flask, render_template,request,redirect,url_for
import mysql.connector
app=Flask(__name__)
try:
  connection=mysql.connector.connect(
                     host='localhost',
                     port=int(3306),
                     user='root',
                     password='P@vsql321',
                     db='New_1',
                     )
  Cursor=connection.cursor()
except mysql.connector.Error as e:
    print('Error connectinng to MYSQL:',e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/display',methods=['POST','GET'])
def display():
    if request.method=='POST':  
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        mobile=request.form['mobile']
        gender=request.form['gender']
        date=request.form['date']
        comment=request.form['comment']
        try:
          Cursor.execute("INSERT INTO Appointment(fname,lname,email,mobile,gender,date,comment) VALUES (%s, %s,%s,%s,%s,%s,%s)", (fname,lname,email,mobile,gender,date,comment))
          connection.commit()
          return redirect(url_for('dashboard')) 
        except mysql.connector.Error as er:
          print('system error',er)
        return redirect(url_for('dashboard'))
    else:
       pass
@app.route("/dashboard")
def dashboard():
   try:
      Cursor.execute("select * from Appointment ")
      value = Cursor.fetchall()
      return render_template('dashboard.html',data=value)
   except mysql.connector.Error as e:
      print("system error",e)
      return"Error fetching data from the database"
@app.route('/update/<id>')
def update(id):
    Cursor.execute('SELECT * FROM Appointment WHERE id = %s', (id,))
    value = Cursor.fetchone()
    return render_template('edit.html', data=value)

@app.route('/delete/<id>')
def delete(id):
    try:
        Cursor.execute('DELETE FROM Appointment WHERE id = %s', (id,))
        return redirect(url_for('dashboard'))
    except mysql.connector.Error as e:
      print("system error",e)
      return"Error fetching data from the database"

@app.route('/edit_section', methods=['POST', 'GET'])
def edit_section():
    if request.method == 'POST':
        try:
            id = request.form['id']
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            mobile = request.form['mobile']
            gender = request.form['gender']
            date = request.form['date']
            comment = request.form['comment']
            update_query = """
                UPDATE Appointment 
                SET fname=%s, lname=%s, email=%s, mobile=%s, gender=%s, date=%s, comment=%s 
                WHERE id=%s
            """
            Cursor.execute(update_query, (fname, lname, email, mobile, gender,date, comment, id))
            connection.commit()
            return redirect(url_for('dashboard'))
        except mysql.connector.Error as er:
            print('System error:', er)
            return "Database error during update"
    else:
        return "Invalid request method"
if __name__ == '__main__':
    app.run(debug=True)
