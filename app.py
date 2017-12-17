from flask import Flask, request, redirect, session, url_for, render_template, jsonify
import sqlite3
import random
import string

app = Flask(__name__, template_folder='views', static_folder='static')
app.secret_key = '&,mcoiw.28uy785x,236tASAc562mnbsvS@SSj'


class Db:
    connection = None

    @staticmethod
    def init():
        conn = Db.get()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login VARCHAR UNIQUE,
            pwd VARCHAR,
            name VARCHAR DEFAULT 'Not set',
            surname VARCHAR DEFAULT 'Not set',
            email VARCHAR UNIQUE,
            bio TEXT DEFAULT 'Not set',
            activated VARCHAR DEFAULT 'False',
            regtime DATETIME DEFAULT CURRENT_TIMESTAMP,
            gender VARCHAR DEFAULT 'Not set',
            pic VARCHAR DEFAULT 'default.png'   
        );
        """)
        conn.commit()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token VARCHAR
        );
        """)
        conn.commit()

    @staticmethod
    def get():
        """

        :rtype: sqlite3.Connection
        """
        if Db.connection is None:
            Db.connection = sqlite3.connect('db.sqlite3', check_same_thread=False)

        return Db.connection

    @staticmethod
    def get_user(login_email, pwd=None):
        cursor = Db.get().cursor()

        if pwd is None:
            cursor.execute('SELECT id,login,name,surname,email,bio,regtime,pic FROM users '
                           'WHERE login=? OR email=?', (login_email, login_email))
        else:
            cursor.execute('SELECT id,login,name,surname,email,bio,regtime,pic FROM users '
                           'WHERE (login=? AND pwd=?) OR (email=? AND pwd=?)',
                           (login_email, pwd, login_email, pwd))
        result = cursor.fetchall()
        cursor.close()

        if len(result) == 0:
            return None
        if len(result) > 1:
            print("ERROR: 2 users with same login|email '{}'!".format(login_email))
            exit(1)

        result = result.pop()
        usr = {
            'id': result[0],
            'login': result[1],
            'name': result[2],
            'surname': result[3],
            'email': result[4],
            'bio': result[5],
            'regtime': result[6],
            'pic': result[7]
        }

        return usr

    @staticmethod
    def get_user_by_id(id):
        cursor = Db.get().cursor()
        cursor.execute('SELECT id,login,name,surname,email,bio,regtime,pic FROM users WHERE id=?', (id,))
        result = cursor.fetchall()
        cursor.close()

        if len(result) == 0:
            return None
        if len(result) > 1:
            print("ERROR: 2 users with same id '{}'!".format(id))
            exit(1)

        result = result.pop()
        usr = {
            'id': result[0],
            'login': result[1],
            'name': result[2],
            'surname': result[3],
            'email': result[4],
            'bio': result[5],
            'regtime': result[6],
            'pic': result[7]
        }

        return usr

    @staticmethod
    def get_user_by_token(token):
        cursor = Db.get().cursor()
        cursor.execute('SELECT user_id FROM sessions WHERE token=?', (token,))

        result = cursor.fetchall()
        cursor.close()

        if len(result) == 0:
            return None
        if len(result) > 1:
            print("ERROR: 2 identical tokens but they have to be different '{}'!!!".format(token))
            exit(1)

        result = result.pop()
        user_id = result[0]
        usr = Db.get_user_by_id(user_id)

        return usr

    @staticmethod
    def get_user_by_session():
        return Db.get_user_by_token(session['token']) if 'token' in session else None

    @staticmethod
    def sign_in(login, pwd):
        usr = Db.get_user(login, pwd)

        if usr is None:
            return None

        token = Db.generate_token(usr['id'])

        if token is False:
            return None
        return token

    @staticmethod
    def sign_up(login, email, name, surname, gender, pwd):
        token = session.pop('token', None)

        if token is not None:
            print("WARNING: Signing up with token available! Retiring current token and proceeding...")
            Db.delete_token(token)

        name = 'Not set' if name == '' else name
        surname = 'Not set' if surname == '' else surname

        login_check = True if Db.get_user(login) is None else False
        email_check = True if Db.get_user(email) is None else False

        if not login_check or not email_check:
            print("False: LOGIN({}) OR EMAIL({}) is already exists!".format(login, email))
            return False

        if len(pwd) < 6:
            print("False: Password is too short!".format(len(pwd)))
            return False

        cursor = Db.get().cursor()
        cursor.execute("INSERT INTO users (login,email,name,surname,gender,pwd) VALUES (?,?,?,?,?,?)",
                       (login, email, name, surname, gender, pwd))
        Db.get().commit()
        cursor.execute('SELECT changes()')
        changes = cursor.fetchone()
        success = changes[0] > 0
        cursor.close()

        if success:
            usr = Db.get_user(login)
            usr_id = False if usr is None else usr['id']

            if usr_id is None:
                print("INSERT successfull but error in token generating...")
                return False
            session['token'] = Db.generate_token(usr_id)

        return success


    @staticmethod
    def generate_token(id):
        """
        Generates token and inserts it into `tokens` table
        :param id: id of person who needs token
        :return: False in case of error | String with token in case of success
        """
        token = ''.join([random.choice(string.ascii_letters + string.digits) for ignored in range(32)])

        cursor = Db.get().cursor()
        cursor.execute('INSERT INTO sessions (user_id,token) VALUES (?, ?)', (id, token))
        Db.get().commit()
        cursor.execute('SELECT changes()')
        changes = cursor.fetchone()
        success = changes[0] > 0
        cursor.close()

        return token if success else False

    @staticmethod
    def delete_token(token=None):
        token = session.pop('token', None) if token is None else token

        if token is None:
            print("WARNING: token is None. Returned True")
            return True

        cursor = Db.get().cursor()
        cursor.execute('DELETE FROM sessions WHERE token=?', (token,))
        Db.get().commit()
        cursor.execute('SELECT changes()')
        changes = cursor.fetchone()
        success = changes[0] == 1
        cursor.close()

        print("{}: Deleted tokens - {}".format("SUCCESS" if success else "ERROR", changes[0]))
        return success


    @staticmethod
    def close():
        if Db.connection is not None:
            Db.connection.close()
            Db.connection = None


@app.route('/')
def index():
    data = {
        'user': Db.get_user_by_session()
    }

    return render_template('index.html', **data)


@app.route('/profile/<login>')
def user(login):
    data = {
        'user': Db.get_user_by_session(),
        'profile': Db.get_user(login)
    }
    return render_template('profile.html', **data)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    data = {
        'user': Db.get_user_by_session()
    }

    if data['user'] is not None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        login = request.form.get('login_email', None)
        pwd = request.form.get('pwd', None)

        token = Db.sign_in(login, pwd)
        if token:
            session['token'] = token
            print(token)

        return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('sign_in.html', **data)


@app.route('/sign_up', methods=['POST'])
def sign_up():
    data = {
        'user': Db.get_user_by_session()
    }

    if data['user'] is not None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        for key, value in request.form.items():
            print("\t{}: {}".format(key, value))

        login = request.form.get('login', None)
        email = request.form.get('email', None)
        name = request.form.get('name', None)
        surname = request.form.get('surname', None)
        gender = request.form.get('gender', None)
        pwd = request.form.get('pwd', None)

        if login is None or email is None or name is None or surname is None or gender is None or pwd is None:
            return jsonify(status='ERR', err_description='<b>Not full list of arguments!</b><br>'
                                                         'Expecting login,email,name,surname,gender,pwd!')

        result = Db.sign_up(login, email, name, surname, gender, pwd)

        if result:
            return jsonify(status='OK')
        else:
            return jsonify(status='ERR')


@app.route('/ajax/<action>', methods=['GET'])
def ajax(action):
    if action == 'check-login':
        login = request.args.get('login', None)

        if login is None:
            return jsonify(status='ERR', err_description='No login specified')

        result = Db.get_user(login)

        return jsonify(status='OK', login_status=('free' if result is None else 'taken'))


@app.route('/logout')
def logout():
    Db.delete_token()
    return redirect(url_for('index'))


if __name__ == '__main__':
    Db.init()
    app.run(debug=True)
