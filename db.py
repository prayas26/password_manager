import pymysql.cursors
import genpass

class Database(object):
    def __init__(self):
        self.host = "localhost"
        self.usrnme = "root"
        self.pswrd = ""  
        self.dbnme = "smart_password"
        self.connection = pymysql.connect(host=self.host,
                             user=self.usrnme,
                             password=self.pswrd,
                             db=self.dbnme,
                             cursorclass=pymysql.cursors.DictCursor)

    def con_auth(self, mobile, user_pass):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM users WHERE userid='"+mobile+"'"
            cursor.execute(com)
            check = cursor.fetchone()
        self.connection.commit()
        try:
            userpass = check["password"]
            if genpass.check_password_hash(userpass, user_pass):
                return check

        except:
            return None

    def register_user(self, mobile, user_pass, username):
        with self.connection.cursor() as cursor:
            hash_pass = genpass.User(mobile, user_pass)
            hash_pass = hash_pass.pw_hash
            com = "INSERT INTO users VALUES ('"+mobile+"', '"+hash_pass+"', '"+username+"', 'user')"
            cursor.execute(com)
            check = cursor.fetchone()
        self.connection.commit()

    def register_admin(self, adminID, adminPass):
        with self.connection.cursor() as cursor:
            hash_pass = genpass.User(adminID, adminPass)
            hash_pass = hash_pass.pw_hash
            com = "INSERT INTO users VALUES ('"+adminID+"', '"+hash_pass+"', 'admin', 'admin')"
            cursor.execute(com)
            check = cursor.fetchone()
        self.connection.commit()

    def addbill(self, uniqueid, cost, userid):
        with self.connection.cursor() as cursor:
            com = "INSERT INTO reimbursement VALUES ('"+uniqueid+"', '"+cost+"', '"+userid+"', 'pending')"
            cursor.execute(com)
        self.connection.commit()

    def getInfo(self, mobile, status):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM reimbursement WHERE userid='"+mobile+"' AND status='"+status+"'"
            cursor.execute(com)
            check = cursor.fetchall()
        self.connection.commit()
        return check

    def checkUser(self, userid):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM users WHERE userid='"+userid+"'"
            cursor.execute(com)
            check = cursor.fetchone()
        self.connection.commit()
        return check

    def getBills(self, status):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM reimbursement WHERE status='"+status+"'"
            cursor.execute(com)
            check = cursor.fetchall()
        self.connection.commit()
        return check

    def closeRequest(self, uniqueid):
        with self.connection.cursor() as cursor:
            com = "UPDATE reimbursement SET status='complete' WHERE uniqueid='"+uniqueid+"'"
            try:
                cursor.execute(com)
                self.connection.commit()
                return "complete"
            except:
                return "error"