from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your secret key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
                     port=int(3306),
                     user='root',
                     password='P@vsql321',
                     db='voting_system'
    )
    return connection

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            qry = "SELECT * FROM admin1 WHERE username = %s AND password = %s"
            cursor.execute(qry, (username, password))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['admin_id'] = account['admin_id']
                session['email']=account['email']
                
                session['role'] = account['role']
                msg = 'Logged in successfully!'
                if session['role']=='admin':
                    return redirect(url_for('admin_dashboard'))
                elif session['role']=='voter':
                    return redirect(url_for('home'))
                else:
                    msg='Unknown role!'
            else:
                msg = 'Incorrect username/password!'
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            msg = 'An error occurred. Please try again later.'
        finally:
            cursor.close()
            connection.close()
    return render_template('login.html', msg=msg)

@app.route('/Sign_up', methods=['GET', 'POST'])
def Sign_up():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        email=request.form['email']
        password = request.form['password']
        role=request.form['role']
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM admin1 WHERE username = %s", (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                cursor.execute("INSERT INTO admin1 (username,email, password,role) VALUES (%s,%s, %s,%s)", (username,email, password,role))
                connection.commit()
                msg = 'You have successfully registered!'
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            msg = 'An error occurred. Please try again later.'
        finally:
            cursor.close()
            connection.close()
    return render_template('Sign_up.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('admin_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COUNT(*) AS count FROM polls1")
            poll_count = cursor.fetchone()['count']
            print('count',poll_count)
            cursor.execute("SELECT COUNT(*) AS count FROM votes")
            result_count = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) AS count FROM users")
            users_count = cursor.fetchone()['count']

        
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            poll_count = result_count=users_count  = 0
        finally:
            cursor.close()
            connection.close()
        
        return render_template('admin_dashboard.html', poll_count=poll_count, result_count=result_count,users_count=users_count)
    else:
        return redirect(url_for('login'))
@app.route('/admin/polls/create', methods=['GET', 'POST'])
def create_poll():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO polls1 (title, description) VALUES (%s, %s)", (title, description))
        connection.commit()
        cursor.close()
        return redirect(url_for('view_polls'))
    return render_template('create_poll.html')

@app.route('/admin/polls/edit/<int:poll_id>', methods=['GET', 'POST'])
def edit_poll(poll_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM polls1 WHERE poll_id = %s", (poll_id,))
    poll = cursor.fetchone()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        cursor.execute("UPDATE polls1 SET title = %s, description = %s WHERE poll_id = %s", (title, description, poll_id))
        connection.commit()
        cursor.close()
        return redirect(url_for('view_polls'))
    cursor.close()
    return render_template('edit_poll.html', poll=poll)

@app.route('/admin/polls/delete/<int:poll_id>', methods=['POST'])
def delete_poll(poll_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM polls1 WHERE poll_id = %s", (poll_id,))
    connection.commit()
    cursor.close()
    return redirect(url_for('view_polls'))

# @app.route('/question/<int:poll_id>', methods=['GET', 'POST'])
# def question(poll_id):
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     if request.method == 'POST':       
#         option1 = request.form['option1']
#         option2 = request.form['option2']
#         cursor.execute("INSERT INTO options (poll_id, option_text) VALUES (%s, %s)", (poll_id, option1))
#         cursor.execute("INSERT INTO options (poll_id, option_text) VALUES (%s, %s)", (poll_id, option2))
#         # Insert more options
#         connection.commit()
#         cursor.close()
#         return redirect(url_for('question'))
#     return render_template('question.html')

# @app.route('/question', methods=['GET', 'POST'])
# def question():
#     if 'loggedin' in session:
#         connection = get_db_connection()
#         cursor = connection.cursor(dictionary=True)

#         if request.method == 'POST':
#             poll_id=request.form['poll_id']   
#             question=request.form['question']
#             option1 = request.form['option1']
#             option2 = request.form['option2']
#             try:
#                 cursor.execute("INSERT INTO options (poll_id,question,option1,option2) VALUES (%s,%s,%s, %s)", (poll_id,question, option1,option2))
                
#                 connection.commit()
#                 flash('Question added successfully!')
#                 return redirect(url_for('que_display', poll_id=poll_id))
#             except mysql.connector.Error as e:
#                 print("Error executing SQL query:", e)
#                 flash('An error occurred. Please try again later.')
#             finally:
#                 cursor.close()
#                 connection.close()

#         else:
#             try:
#                 cursor.execute("SELECT poll_id, title FROM polls1")
#                 qu = cursor.fetchall()
#             except mysql.connector.Error as e:
#                 print("Error executing SQL query:", e)
#                 qu = []
#             finally:
#                 cursor.close()
#                 connection.close()
#             return render_template('question.html', qu=qu)
#     else:
#         return redirect(url_for('login'))
    
@app.route('/question', methods=['GET', 'POST'])
def question():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == 'POST':
            poll_id = request.form['poll_id']   
            question = request.form['question']
            option1 = request.form['option1']
            option2 = request.form['option2']
            
            print(f"Received data - Poll ID: {poll_id}, Question: {question}, Option1: {option1}, Option2: {option2}")  # Debugging

            try:
                cursor.execute("INSERT INTO options (poll_id, question, option1, option2) VALUES (%s, %s, %s, %s)", (poll_id, question, option1, option2))
                connection.commit()
                flash('Question added successfully!')
                return redirect(url_for('que_display', poll_id=poll_id))
            except mysql.connector.Error as e:
                print("Error executing SQL query:", e)
                flash('An error occurred. Please try again later.')
            finally:
                cursor.close()
                connection.close()
        else:
            try:
                cursor.execute("SELECT poll_id, title FROM polls1")
                qu = cursor.fetchall()
                print(qu)  # Debugging
            except mysql.connector.Error as e:
                print("Error executing SQL query:", e)
                qu = []
            finally:
                cursor.close()
                connection.close()
            return render_template('question.html', qu=qu)
    else:
        return redirect(url_for('login'))


@app.route('/que_display/<int:poll_id>', methods=['GET', 'POST'])
def que_display(poll_id):
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT o.poll_id,o.question, o.option1,o.option2, p.title FROM options o INNER JOIN polls1 p ON o.poll_id = p.poll_id WHERE o.poll_id = %s", (poll_id,))
            que = cursor.fetchall()
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            que = []
        finally:
            cursor.close()
            connection.close()
        return render_template('que_display.html', que=que)
    else:
        return redirect(url_for('login'))

@app.route('/admin/polls')
def view_polls():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM polls1")
            polls = cursor.fetchall()
            print('polls', polls)  # Debugging: Print polls to console
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
        finally:
            cursor.close()
            connection.close()  # Close the connection after use
    else:
        polls = []
    return render_template('view_polls.html', polls=polls)


@app.route('/admin/users')
def manage_users():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
        finally:
            cursor.close()
            connection.close()  # Close the connection after use
    else:
        users = []
    return render_template('manage_users.html', users=users)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                cursor.execute("UPDATE users SET username = %s, password = %s WHERE user_id = %s",
                               (username, password, user_id))
                connection.commit()
                return redirect(url_for('manage_users'))
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
        finally:
            cursor.close()
            connection.close()
    return render_template('edit_user.html', user=user)
#
@app.route('/admin/users/delete/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    connection.commit()
    cursor.close()
    return redirect(url_for('manage_users'))
@app.route('/home')
def home():
    return render_template('home.html')
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('profile'))
        else:
            return 'Invalid credentials'
    return render_template('user_login.html')

@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        connection.commit()
        return redirect(url_for('user_login'))
    return render_template('user_register.html')

@app.route('/user_logout')
def user_logout():
    session.pop('user_id', None)
    return redirect(url_for('Sign_up'))

@app.route('/profile')
def profile():
    
    if 'user_id' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
            user = cursor.fetchall()
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            user = None
        finally:
            cursor.close()
            connection.close()
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('user_login'))


@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    if 'user_id' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
    user = cursor.fetchone()
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        cursor.execute("UPDATE users SET username= %s, password= %s WHERE user_id = %s", (user_id,username,password))
        connection.commit()
        cursor.close()
        return redirect(url_for('profile'))
    cursor.close()
    return render_template('edit_profile.html', user=user)
@app.route('/polls')
def polls():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
                cursor.execute("select * from polls1")
                value = cursor.fetchall()
                return render_template('polls.html',value=value)
    except mysql.connector.Error as e:
       print("system error",e)


@app.route('/vote/<int:poll_id>', methods=['GET', 'POST'])
def vote(poll_id):

    print(poll_id)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM polls1 WHERE poll_id = %s', (poll_id,))
    polls = cursor.fetchone()
    
    cursor.execute('SELECT * FROM options WHERE poll_id = %s', (poll_id,))
    questions = cursor.fetchall()
    print(questions)
    #   print("topics: ",topics[0][1])
    
    
        #   connection.close()
    return render_template('vote.html', polls=polls,questions=questions)

@app.route('/results<int:poll_id>')
def results(poll_id):
    msg=''
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT o.poll_id,o.question, COUNT(v.poll_id) AS votes FROM options o LEFT JOIN votes v ON o.option_id = v.option_id WHERE o.poll_id = %s GROUP BY o.option_id', (poll_id,))
    results = cursor.fetchall()
    msg='Vote Done'
    return render_template('results.html', results=results,msg=msg)
          # Handle database errors



if __name__ == '__main__':
    app.run(debug=True)
