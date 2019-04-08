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

    def getUserPassword(self, mobile):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM u"+mobile+""
            cursor.execute(com)
            check = cursor.fetchall()
        self.connection.commit()
        return check

    def createUserDB(self, mobile):
        with self.connection.cursor() as cursor:
            com = """CREATE TABLE u"""+mobile+"""
                (website char(50) NOT NULL,
                username char(50) NOT NULL,
                userpass char(200) NOT NULL);"""
            cursor.execute(com)
    
    def createTeamDB(self, team):
        with self.connection.cursor() as cursor:
            com = """CREATE TABLE t_"""+team+"""
                (website char(50) NOT NULL,
                username char(50) NOT NULL,
                userpass char(200) NOT NULL);"""
            cursor.execute(com)

    def addUserPassword(self, website, userID, userPass, mobile):
        with self.connection.cursor() as cursor:
            userPass = genpass.User(mobile, userPass)
            userPass = userPass.pw_hash
            com = "INSERT into u"+mobile+" VALUES('"+website+"', '"+userID+"', '"+userPass+"')"
            cursor.execute(com)
        self.connection.commit()

    def checkUser(self, userid):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM users WHERE userid='"+userid+"'"
            cursor.execute(com)
            check = cursor.fetchone()
        self.connection.commit()
        return check

    def checkTeam(self, teamid):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM teams WHERE teamName='"+teamid+"'"
            cursor.execute(com)
            check = cursor.fetchone()
        self.connection.commit()
        return check

    def addToTeam(self, team, user, userType):
        with self.connection.cursor() as cursor:
            com = "INSERT into teams VALUES('"+team+"', '"+user+"', '"+userType+"')"
            cursor.execute(com)
        self.connection.commit()

    def checkUserTeams(self, userid):
        with self.connection.cursor() as cursor:
            com = "SELECT * from teams WHERE userid='"+userid+"'"
            cursor.execute(com)
            check = cursor.fetchall()
        return check

    def checkTeamAccess(self, userid, teamName):
        with self.connection.cursor() as cursor:
            com = "SELECT * from teams WHERE userid='"+userid+"' and teamName='"+teamName+"'"
            cursor.execute(com)
            check = cursor.fetchone()
        return check

    def getTeamPassword(self, team):
        with self.connection.cursor() as cursor:
            com = "SELECT * FROM t_"+team+""
            cursor.execute(com)
            check = cursor.fetchall()
        self.connection.commit()
        return check

    def removeTeam(self, teamName):
        with self.connection.cursor() as cursor:
            com = "DELETE from teams WHERE teamName='"+teamName+"'"
            cursor.execute(com)
        self.connection.commit()        

    def deleteTeam(self, teamName):
        with self.connection.cursor() as cursor:
            com = "DROP table t_"+teamName
            cursor.execute(com)
        self.connection.commit()
        self.removeTeam(teamName)

    def retrievePassword(self, mobile, website, username):
        with self.connection.cursor() as cursor:
            com = "SELECT userpass from u"+mobile+" WHERE website='"+website+"' and username='"+username+"'"
            cursor.execute(com)
            checkPass = cursor.fetchone()
        return checkPass