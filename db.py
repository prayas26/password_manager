import pymysql.cursors
import genpass

class Database(object):
    def __init__(self):
        self.host = "localhost"
        self.usrnme = "root"
        self.pswrd = ""
        self.dbnme = "passwordMan"
        self.connection = pymysql.connect(host=self.host,
                             user=self.usrnme,
                             password=self.pswrd,
                             db=self.dbnme,
                             cursorclass=pymysql.cursors.DictCursor)

    def con_auth(self, user_id, user_pass):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM users WHERE userid='"+user_id+"'"
            cursor.execute(com)
            check = cursor.fetchone()
        self.connection.commit()
        try:
            userpass = check["password"]
            if genpass.check_password_hash(userpass, user_pass):
                return check

        except:
            return None

    def register_user(self, userid, mobile, user_pass):
        with self.connection.cursor() as cursor:
            hash_pass = genpass.User(userid, user_pass)
            hash_pass = hash_pass.pw_hash
            com = "INSERT INTO users VALUES ('"+userid+"', '"+mobile+"', '"+hash_pass+"')"
            cursor.execute(com)
        self.connection.commit()

    def check_id(self, userid, mobile):
        with self.connection.cursor() as cursor:
            com = "SELECT * from users where mobile='"+mobile+"' or userid='"+userid+"'"
            cursor.execute(com)
            check = cursor.fetchone()
        self.connection.commit()
        return check        