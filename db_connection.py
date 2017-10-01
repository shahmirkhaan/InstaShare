import MySQLdb


class DbConnection(object):
    def __init__(self):
        self.db = 0
        self.cursor = 0

    def connect(self):
        self.db = MySQLdb.connect("localhost", "root", "", "instasharedemo")
        self.cursor = self.db.cursor()

    def close(self):
        self.db.close()

    def runQuery(self, sql, p=0):
        self.connect()
        if type(sql) == type([]) and p == 0:
            for query in sql:
                self.cursor.execute(query)
        elif p!=0:
            self.cursor.execute(sql, ("%%"+p+"%%",))
        else:
            self.cursor.execute(sql)
            if sql[:6] == "SELECT":
                return self.cursor.fetchall()
        self.db.commit()
        self.close()
        pass


class Postsdb(object):
    def __init__(self):
        self.db = DbConnection()
        self.picture_db = Picturesdb()

    def get_picture_id(self, post_id):
        return self.db.runQuery("SELECT picture_id FROM post_info WHERE post_id = {x} ".format(x=post_id))

    def get_username(self, post_id):
        return self.db.runQuery("SELECT username FROM post_info WHERE post_id = {x} ".format(x=post_id))

    def if_liked(self, username, post_id):
         return len(self.db.runQuery("SELECT liked_username FROM post_liked_by WHERE post_id = {x} AND liked_username = '{y}'".format(x=post_id, y=username))) > 0

    def get_caption(self, post_id):
        return self.db.runQuery("SELECT caption FROM post_info WHERE post_id = {x} ".format(x=post_id))

    def get_comment_id(self, post_id):
        return self.db.runQuery("SELECT comment_id FROM post_comment_like WHERE post_id = {x} ".format(x=post_id))

    def unlike_post(self, post_id, username):
        self.db.runQuery([
            "DELETE FROM post_liked_by WHERE post_id={x} AND liked_username = '{y}'".format(x=post_id, y=username),
            "UPDATE post_likes SET likes = likes - 1 WHERE post_id = {}".format(post_id)])

    def like_post(self, post_id, username):
        self.db.runQuery(["UPDATE post_likes SET likes = likes + 1 WHERE post_id = {}".format(post_id),
                          "INSERT INTO post_liked_by(post_id,liked_username) VALUES({x},'{y}'"
                          ")".format(x=post_id, y=username)])

    def comment(self, comment):
        self.db.runQuery(["INSERT INTO comment_body(body, time, date) VALUES('{x}',CURRENT_TIME(), "
                         "CURRENT_DATE())".format(x=comment[2]),
                          "INSERT INTO post_comment_like(post_id,comment_username,comment_id) "
                          "VALUES({x},'{y}',(SELECT comment_id FROM comment_body WHERE date = CURRENT_DATE()"
                          "AND time = CURRENT_TIME() AND body = '{z}'))".format(x=comment[0],y=comment[1], z=comment[2])])

    def create_post(self, post):
        self.picture_db.insert_into(post[0])
        self.db.runQuery("INSERT INTO post_info(username,caption,picture_id) VALUES('{x}','{y}',"
                         "(SELECT picture_id FROM pictures WHERE picture = '{z}'))".format(x=post[1], y=post[2], z=post[0]))

    def create_likes(self, post_id):
        self.db.runQuery("INSERT INTO post_likes(post_id) VALUES({})".format(post_id))

    def get_post_of_following(self,username):
        return self.db.runQuery("SELECT post_id FROM post_info WHERE username IN "
                                "(SELECT following_username FROM following WHERE username = '{}')".format(username))

    def get_posts(self, username):
        return self.db.runQuery("SELECT post_id FROM post_info WHERE username ='{}'".format(username))

    def get_info_post(self,post_id):
        return self.db.runQuery("SELECT * FROM post_info WHERE post_id = {}".format(post_id))

    def get_likes(self,post_id):
        return self.db.runQuery("SELECT liked_username FROM post_liked_by WHERE post_id = {}".format(post_id))

    def get_likes_count(self,post_id):
        return self.db.runQuery("SELECT likes FROM post_likes WHERE post_id = {}".format(post_id))

    def get_comment_body(self, comment_id):
        return self.db.runQuery("SELECT body FROM comment_body WHERE comment_id = {}".format(comment_id))

    def get_comment_by(self, comment_id):
        return self.db.runQuery("SELECT comment_username FROM post_comment_like WHERE comment_id = {}".format(comment_id))


class Chat(object):
    def __init__(self):
        self.db = DbConnection()

    def get_info(self, identifier):
        return self.db.runQuery("SELECT * FROM chat WHERE identifer = {x}".format(x=identifier))

    def getChats(self,username):
        return self.db.runQuery("SELECT identifer FROM chat WHERE user1 = '{x}' OR user2 = '{x}'".format(x=username))

    def getMessages(self,identifier):
        return self.db.runQuery("SELECT body, username, msg_num FROM messages WHERE identifer = {} ORDER BY msg_num".format(identifier))

    def createChat(self, user1, user2):
        self.db.runQuery("INSERT INTO chat(user1,user2) VALUES('{}','{}')".format(user1, user2))

    def get_total_msg(self,identifier):
        return self.db.runQuery("SELECT total_messages FROM chat WHERE identifer = {x}".format(x=identifier))

    def sendMessage(self, body, username, identifier):
        self.db.runQuery("UPDATE chat SET total_messages = total_messages + 1 WHERE identifer = {}".format(identifier))
        self.db.runQuery("INSERT INTO messages(identifer, msg_num, body, username, date, time) "
                         "VALUES({x},(SELECT total_messages FROM chat WHERE identifer = {x}),'{y}'"
                         ",'{z}',CURRENT_DATE(),CURRENT_TIME())".format(x=identifier, y=body, z=username))


class Stories(object):
    def __init__(self):
        self.db = DbConnection()

    def get_story(self, username):
        return self.db.runQuery("SELECT picture, caption FROM story WHERE username = '{x}'"
                                " AND date < TIMESTAMPADD(HOUR, 24, NOW())"
                                .format(x=username))

    def insert_into(self, info):
        self.db.runQuery(
            "INSERT INTO story(username,picture,caption) VALUES('{a}','{b}'"
            ",'{e}')".format
            (a=info[0], b=info[1], e=info[2]))

    def get_picture_user(self, username):
        return self.db.runQuery("SELECT picture FROM story WHERE username = '{x}'"
                                "  AND CURRENT_TIME()- time> 0 ORDER BY time ASC".format(x=username))

    def get_date_user(self, username):
        return self.db.runQuery("SELECT date FROM story WHERE username = '{x}'  "
                                "AND CURRENT_TIME()- time> 0 ORDER BY time ASC".format(x=username))

    def get_time_user(self, username):
        return self.db.runQuery("SELECT time FROM story WHERE username = '{x}'  "
                                "AND CURRENT_TIME()-time> 0 ORDER BY time ASC".format(x=username))


class Picturesdb(object):
    def __init__(self):
        self.db = DbConnection()

    def get_picture_id(self, picture):
        return self.db.runQuery("SELECT picture_id FROM pictures WHERE picture = '{x}'".format(x=picture))

    def insert_into(self, picture):
        self.db.runQuery("INSERT INTO pictures(date,time,picture) VALUES(CURRENT_DATE(),CURRENT_TIME(),'{z}')".format(z=picture))

    def get_picture(self, picture_id):
        return self.db.runQuery("SELECT picture FROM pictures WHERE picture_id = {x}".format(x=picture_id))

    def get_datee(self, picture_id):
        return self.db.runQuery("SELECT date FROM pictures WHERE picture_id = {x}".format(x=picture_id))[0][0]

    def get_time(self, picture_id):
        return self.db.runQuery("SELECT time FROM pictures WHERE picture_id = {x}".format(x=picture_id))[0][0]


class Userdb(object):

    def __init__(self):
        self.db = DbConnection()

    def getUsernameLogin(self,password,username):
        return self.db.runQuery("SELECT username FROM user_info where email= ANY"
                                "(SELECT email FROM emailpassword where password ='{x}') AND username = '{y}'".format(x=password , y=username))

    def getFollowing(self, username):
        return self.db.runQuery("SELECT following_username FROM following where username='{x}'".format(x=username))

    def getFollowers(self, username):
        return self.db.runQuery("SELECT username FROM following where following_username='{x}'".format(x=username))

    def getPass(self, email):
        return self.db.runQuery("SELECT password FROM emailpassword where email='{x}'".format(x=email))

    def getInfo(self,username):
        return self.db.runQuery("SELECT * FROM user_info where username='{x}'".format(x=username))

    def getADPass(self, adminName):
        return self.db.runQuery("SELECT admin_pass FROM admin where admin_name='{x}'".format(x=adminName))

    def getLocation(self, phoneNo):
        return self.db.runQuery("SELECT location FROM phonelocation where phone_no={x}".format(x=phoneNo))

    def getLink(self, picture):
        return self.db.runQuery("SELECT link FROM picturelink where picture_id={x}".format(x=picture))

    def getUser(self,username):
        return self.db.runQuery("SELECT username FROM user_info WHERE username = '{}'".format(username))

    def insertInto(self, info):
        self.db.runQuery(["INSERT INTO user_info(username,email,name,phone_no,DOB,picture_id,gender,admin_name,bio,following_count)" \
               " VALUES('{a}','{b}','{c}',{d},'{e}',{f},'{g}','{h}','{i}',{j})" \
               "".format(a=info[0], b=info[1], c=info[2], d=info[3], e=info[4],
                         f=info[5], g=info[6], h=info[7], i=info[8], j=info[9]),
                "INSERT INTO emailpassword(email,password) VALUES('{a}','{b}')".format(a=info[1], b=info[10]),
                "INSERT INTO phonelocation(phone_no,location) VALUES({a},'{b}')".format(a=info[3], b=info[11]),
                "INSERT INTO picturelink(picture_id,link) VALUES('{a}','{b}')".format(a=info[5], b=info[13])
                ])

    def checkUsername(self, username):
        return len(self.db.runQuery("SELECT username FROM user_info where username = '{x}'".format(x=username))) == 0

    def checkPhone(self, phone_no):
        return len(self.db.runQuery("SELECT username FROM user_info where phone_no = {x}".format(x=phone_no))) == 0

    def checkEmail(self, email):
        return len(self.db.runQuery("SELECT username FROM user_info where email = '{x}'".format(x=email))) == 0

    def adminInsert(self, username, password):
        self.db.runQuery("INSERT INTO admin(admin_name,admin_pass) VALUES('{a}','{b}')".format(a=username, b=password))

    def updateEmail(self,email,username):
        self.db.runQuery("UPDATE user_info SET email = '{x}' where username = '{y}'".format(x=email, y=username))

    def updatePhoneNo(self, phone_no,username):
        self.db.runQuery("UPDATE user_info SET phone_no = {x} where username = '{y}'".format(x=phone_no, y=username))

    def updatePicture_id(self,picture_id,username):
        self.db.runQuery("UPDATE user_info SET picture_id = {x} where username = '{y}'".format(x=picture_id, y=username))

    def updateBio(self,bio,username):
        self.db.runQuery("UPDATE user_info SET bio = '{x}' where username = '{y}'".format(x=bio, y=username))

    def updateFollowingCount(self,count,username):
        self.db.runQuery("UPDATE user_info SET following_count = {x} where username = '{y}'".format(x=count, y=username))

    def updatePassword(self, password, email):
        self.db.runQuery("UPDATE emailpassword SET password = '{x}' where email = '{y}'".format(x=password, y=email))

    def updateLink(self, link, picture_id):
        self.db.runQuery("UPDATE picturelink SET link = '{x}' where picture_id = {y}".format(x=link, y=picture_id))

    def updateLocation(self,location, phone_no):
        self.db.runQuery("UPDATE phonelocation SET location = '{x}' where phone_no = {y}".format(x=location, y=phone_no))

    def follow(self, username, following):
        self.db.runQuery("UPDATE user_info SET following_count = following_count + 1 where username = '{y}'".format(y=username))
        self.db.runQuery("INSERT INTO following(username,following_username) VALUES( '{x}','{y}')".format(x=username, y=following))

    def unfollow(self, username, following):
        self.db.runQuery(
            "UPDATE user_info SET following_count = following_count - 1 where username = '{y}'".format(y=username))
        return self.db.runQuery("DELETE FROM following WHERE following_username = '{x}' AND username = '{y}'".format(y=username, x=following))


class Notification(object):
    def __init__(self):
        self.db = DbConnection()

    def insert(self, username_by, username_for, type_of, at):
        self.db.runQuery(
            "INSERT INTO notification(username_for, username_by, type, at) VALUES( '{x}','{y}','{z}', {a})".format
            (x=username_by, y=username_for, z=type_of, a=at))

    def get_notification(self, id):
        self.db.runQuery(
            "SELECT username_by, type, at FROM notification WHERE username_for = '{z}')".format(z=id))

    def get_id(self, username_for):
        self.db.runQuery(
            "SELECT id FROM notification WHERE username_for = '{z}')".format(z=id))
