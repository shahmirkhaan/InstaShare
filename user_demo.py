import db_connection


class user_demo(object):
    def __init__(self, username):
        self.db = db_connection.Userdb()
        self.pdb = db_connection.Postsdb()
        self.sdb = db_connection.Stories()
        self.db = db_connection.Userdb()
        self.pdb = db_connection.Postsdb()
        self.sdb = db_connection.Stories()
        result = self.db.getInfo(username)
        self.username=result[0][0]
        self.dob = result[0][4]
        self.picture_id = result[0][5]
        self.phone_no = result[0][3]
        self.name = result[0][2]
        self.location = self.db.getLocation(self.phone_no)[0][0]
        self.bio = result[0][8]
        self.link = self.db.getLink(self.picture_id)[0][0]
        self.followingCount = result[0][9]
        self.followerCount = len(self.db.getFollowers(self.username))
        self.post_ids = self.pdb.get_posts(self.username)
        self.stories = self.sdb.get_story(self.username)

    def get_picture_id(self):
        return self.picture_id

    def set_picture(self, picture):
        db = db_connection.Picturesdb()
        db.insert_into(picture)
        id = db.get_picture_id(picture)[0][0]
        self.db.updatePicture_id(id, self.username)
        self.picture_id = id

    def update(self):
        result = self.db.getInfo(self.username)
        self.username = result[0][0]
        self.dob = result[0][4]
        self.picture_id = result[0][5]
        self.phone_no = result[0][3]
        self.name = result[0][2]
        self.location = self.db.getLocation(self.phone_no)[0][0]
        self.bio = result[0][8]
        self.link = self.db.getLink(self.picture_id)[0][0]
        self.followingCount = result[0][9]
        self.followerCount = len(self.db.getFollowers(self.username))
        self.post_ids = self.pdb.get_posts(self.username)
        self.stories = self.sdb.get_story(self.username)

    def check_stories(self):
        return len(self.stories) != 0

    def get_post_ids(self):
        postids = []
        for (result,) in self.post_ids:
            postids.append(result)
        return postids

    def get_stories(self):
        return self.stories

    def getUsername(self):
        return self.username

    def getDOB(self):
        return self.dob

    def getLocation(self):
        return self.location

    def getBio(self):
        return self.bio

    def getLink(self):
        return self.link

    def getFollowing(self):
        return self.followingCount

    def getFollower(self):
        return self.followerCount

    def getName(self):
        return self.name


class personal(user_demo):
    def __init__(self):
        self.chatsdb = db_connection.Chat()
        self.email = 0
        self.password = 0
        self.chats = 0

    def search(self, info):
        print(info)
        results = self.db.getUser(info)
        if len(results) == 0:
            return 0
        return results

    def update(self):
        user_demo.update(self)
        self.chats = self.chatsdb.getChats(self.username)

    def get_wall(self):
        results = self.pdb.get_post_of_following(self.username)
        postids = [result for (result,) in results]
        for (result,) in self.post_ids:
            postids.append(result)


        return postids

    def add_story(self, picture, cap):
        self.sdb.insert_into([self.username, picture, cap])

    def follow(self,username):
        self.db.follow(self.username,username)

    def unfollow(self,username):
        self.db.unfollow(self.username, username)

    def set_user(self, username):
        user_demo.__init__(self, username)
        self.email = self.db.getInfo(self.username)[0][1]
        self.password = self.db.getPass(self.email)
        self.chats = self.chatsdb.getChats(self.username)

    def check_if_following(self, username):
        if username == self.username:
            return True
        results = self.db.getFollowing(self.username)
        print(results)
        for (result,) in results:
            if result == username:
                return True
        return False

    def createChat(self, username):
        self.chatsdb.createChat(self.username, username)

    def post(self, picture, caption):
        self.pdb.create_post([picture, self.username, caption])

    def like(self, post_id):
        if len(self.pdb.get_likes_count(post_id)) == 0:
            self.pdb.create_likes(post_id)
        if self.if_post_liked(post_id):
            self.pdb.unlike_post(post_id, self.username)
        else:
            self.pdb.like_post(post_id, self.username)

    def getEmail(self):
        return self.email

    def check_if_chat_exist(self, username):
        self.update()
        ids = self.get_chat_ids()
        print(ids)
        for i_d in ids:
            print(i_d)
            chat = Chat(i_d, self.username)
            print(chat.chat_with())
            if chat.chat_with() == username:
                return i_d
        self.createChat(username)
        self.update()
        ids = self.get_chat_ids()
        for i_d in ids:
            print(i_d)
            chat = Chat(i_d, self.username)
            print(chat.chat_with())
            if chat.chat_with() == username:
                return i_d

    def getPassword(self):
        return self.password

    def setEmail(self,email):
        self.email = email
        self.db.updateEmail(self.email, self.username)

    def if_post_liked(self, post_id):
        db = db_connection.Postsdb()
        return db.if_liked(self.username, post_id)

    def setPassword(self, password):
        self.password = password
        self.db.updatePassword(self.password, self.email)

    def setLocation(self, location):
        self.location = location
        self.db.updateLocation(self.location, self.phone_no)

    def get_chat_ids(self):
        ids = []
        for (id,) in self.chats:
            ids.append(id)
        return ids

    def setBio(self, bio):
        self.bio = bio
        self.db.updateBio(self.bio, self.username)

    def setLink(self, link):
        self.link = link
        self.db.updateLink(self.link, self.picture_id)

    def setFollowingCount(self):
        self.followingCount = self.followingCount + 1
        self.db.updateFollowingCount(self.followingCount, self.username)

    def setFollowerCount(self, count):
        self.followerCount = count


class Picture(object):
    def __init__(self, picture_id):
        self.picture_id = picture_id
        self.db = db_connection.Picturesdb()
        self.picture = self.db.get_picture(self.picture_id)
        self.date = self.db.get_datee(self.picture_id)
        self.time = self.db.get_time(self.picture_id)

    def get_picture(self):
        return self.picture

    def get_date(self):
        return self.date

    def get_time(self):
        return self.time


class Post(object):
    def __init__(self, post_id, username):
        self.db = db_connection.Postsdb()
        pdb = db_connection.Picturesdb()
        self.post_id = post_id
        self.username = self.db.get_username(self.post_id)
        self.likes = self.db.get_likes_count(self.post_id)
        self.caption = self.db.get_caption(self.post_id)
        comment_id = self.db.get_comment_id(self.post_id)
        self.comment_id = [comment for (comment,) in comment_id]
        print(self.comment_id)
        self.liked = self.db.if_liked(username, self.post_id)
        self.picture_id = self.db.get_picture_id(self.post_id)[0][0]
        print(self.picture_id)
        self.picture = Picture(self.picture_id)

    def get_comment_ids(self):
        return self.comment_id

    def get_info(self):
        if len(self.likes) == 0:
            return [self.username[0][0], 0, self.caption[0][0], self.liked, self.picture.get_picture()[0][0], self.post_id]
        return [self.username[0][0], self.likes[0][0], self.caption[0][0], self.liked, self.picture.get_picture()[0][0],self.post_id]

    def like(self, username):
        if self.liked:
            self.db.like_post(self.post_id, username)
        else:
            self.db.unlike_post(self.post_id, username)

    def comment(self, username, body):
        self.db.comment([self.post_id,username, body])


class Comment(object):
    def __init__(self, comment_id):
        self.db = db_connection.Postsdb()
        self.comment_by = self.db.get_comment_by(comment_id)
        self.comment_body = self.db.get_comment_body(comment_id)

    def get_comment(self):
        return [self.comment_by[0][0], self.comment_body[0][0]]


class Chat(object):
    def __init__(self, identifier, username):
        self.db = db_connection.Chat()
        self.identifier = identifier
        result = self.db.get_info(self.identifier)
        self.total_msg = result[0][1]
        if result[0][2] == username:
            self.username = result[0][2]
            self.user2 = result[0][3]
        elif result[0][3] == username:
            self.username = result[0][3]
            self.user2 = result[0][2]
        self.messages = []

    def add_message(self, body):
        self.db.sendMessage(body, self.username, self.identifier)

    def get_messages_of_chat(self):
        results = self.db.getMessages(self.identifier)
        for result in results:
            self.messages.append([result[0], result[1]])
        return self.messages

    def chat_with(self):
        return self.user2
