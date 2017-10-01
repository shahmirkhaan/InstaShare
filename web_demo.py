
import platform
from flask import Flask,render_template, redirect, request, url_for
import db_connection
import user_demo
from flask_uploads import UploadSet, configure_uploads, IMAGES
from os.path import splitext
import threading
if int(platform.python_version_tuple()[1]) >= 6:
    import asyncio
    import asyncio.base_futures
    import asyncio.base_tasks
    import asyncio.compat
    import asyncio.base_subprocess
    import asyncio.proactor_events
    import asyncio.constants
    import asyncio.selector_events
    import asyncio.windows_utils
    import asyncio.windows_events

    import jinja2.asyncsupport
    import jinja2.ext


app = Flask(__name__)
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
configure_uploads(app, photos)
userdb = db_connection.Userdb()
selfUser = user_demo.personal()


def loginCheck(username, password):
    result = userdb.getUsernameLogin(password,username)
    if len(result) == 0:
        return False
    if result[0][0] == username:
        selfUser.set_user(username)
        return True
    return False


@app.route("/story/<username>")
def stories(username):
    user = user_demo.user_demo(username)
    stories1 = user.get_stories()
    stories = []
    for (picture, caption,) in stories1:
        stories.append([picture, caption, username])
    print(stories)
    return render_template("story.html", posts=stories, username=selfUser.getUsername())


@app.route("/add_story")
def add_story():
    return render_template("make_story.html", username=selfUser.getUsername())


@app.route("/post_story", methods=['POST'])
def post_story():
    file = request.files['input_file']
    filename = photos.save(file)
    print(filename)
    cap = ""
    if request.form.get('caption') != 'none':
        cap = request.form.get('caption')
    selfUser.add_story(filename, cap)
    selfUser.update()
    return redirect(url_for('profile', username=selfUser.getUsername()))


@app.route("/search", methods=['post','get'])
def search():
    if request.method == 'POST':
        result = selfUser.search(request.form.get('inputSearch'))
        if result == 0:
            return render_template("search.html", results=result, found=False, username=selfUser.getUsername(), search="active")
        return render_template("search.html", results=result, Found=True, username=selfUser.getUsername(), search="active")
    return render_template("search.html", Found=True, username=selfUser.getUsername(),search="active")


@app.route("/open_chat/<username>")
def open_chat(username):
    chat_id = selfUser.check_if_chat_exist(username)
    print(chat_id)
    return redirect(url_for('messages', chat_id=chat_id))


@app.route("/comment/<int:post_id>")
def comment(post_id):
    post = user_demo.Post(post_id,selfUser.getUsername())
    ids = post.get_comment_ids()
    comments = []
    for id in ids:
        comment = user_demo.Comment(id)
        comments.append(comment.get_comment())
    selfUser.update()
    return render_template("comments.html", username=selfUser.getUsername(), comments=comments, post_id=post_id)


@app.route("/messages/<int:chat_id>")
def messages(chat_id):
    selfUser.update()
    chat_ids = selfUser.get_chat_ids()
    chats = []
    message = []
    user2 = ''
    for id in chat_ids:
        chat = user_demo.Chat(id, selfUser.getUsername())
        chats.append([id, chat.chat_with()])
        if id == chat_id:
            message = chat.get_messages_of_chat()
            user2 = chat.chat_with()
    return render_template("messages.html", message=message, chats=chats, username=selfUser.getUsername(), user2=user2, chat_id=chat_id, inbox='active')


@app.route("/send_message/<int:chat_id>", methods=['post'])
def send_message(chat_id):
    chat = user_demo.Chat(chat_id, selfUser.getUsername())
    chat.add_message(request.form.get('inputMessage'))
    selfUser.update()
    return redirect(url_for('messages', chat_id=chat_id))


@app.route("/comment_post/<int:post_id>", methods=['POST'])
def comment_post(post_id):
    comment = request.form.get('inputComment')
    if comment:
        post = user_demo.Post(post_id,selfUser.getUsername())
        post.comment(selfUser.username, comment)
    selfUser.update()
    return redirect(url_for('comment', post_id=post_id))


@app.route("/profile/<username>")
def profile(username):
    selfUser.update()
    if username == selfUser.getUsername():
        User = selfUser
    else:
        User = user_demo.user_demo(username)
    ids = User.get_post_ids()
    posts = []
    picture_id = User.get_picture_id()
    picture = ""
    if picture_id == 0:
        picture = 'avatar.png'
    else:
        db = db_connection.Picturesdb()
        picture = db.get_picture(picture_id)[0][0]
    print(picture)
    for id in ids:
        post = user_demo.Post(id, User.getUsername())
        posts.append(post.get_info())
        print(User.check_stories())
    return render_template("profile.html", user="active", info=[User.getName(), User.getUsername(),
                                                                User.getLocation(), User.getFollowing(),
                                                                User.getFollower(), User.getLink(),
                                                                User.getBio(), User.getUsername() != selfUser.getUsername(),
                                                                selfUser.check_if_following(User.getUsername()),
                                                                User.check_stories(), picture], posts=posts, username=selfUser.getUsername())


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/logout")
def logout():
    global selfUser
    selfUser = user_demo.personal()
    return redirect(url_for('index'))


@app.route("/home")
def home():
    selfUser.update()
    ids = selfUser.get_wall()
    posts = []
    for id in ids:
        post = user_demo.Post(id, selfUser.getUsername())
        posts.append(post.get_info())
    print(posts)
    return render_template("home.html", posts=posts, home="active",username=selfUser.getUsername())


@app.route("/make_post")
def make_post():
    return render_template("make_post.html", username=selfUser.getUsername(), heart="active")


@app.route("/edit", methods=['post', 'get'])
def edit():
    if request.method != 'POST':
        return render_template("edit.html", username=selfUser.getUsername(), user="active")
    else:
        if request.form.get('email'):
            if userdb.checkEmail(request.form['email']):
                return render_template("register.html", error=True, eerror=userdb.checkEmail(request.form['email']), )
            selfUser.setEmail(request.form.get('email'))

        if request.files['input_file']:
            file = request.files['input_file']
            filename = photos.save(file)
            selfUser.set_picture(filename)

        if request.form.get('bio'):
            selfUser.setBio(request.form.get('bio'))

        if request.form.get('password'):
            selfUser.setPassword(request.form.get('password'))

        if request.form.get('link'):
            selfUser.setLink(request.form.get('link'))

        if request.form.get('location'):
            selfUser.setLink(request.form.get('location'))

    return redirect(url_for('profile', username=selfUser.getUsername()))


@app.route("/post_post", methods=['POST'])
def post_post():
    file = request.files['input_file']
    filename = photos.save(file)
    fname, ext = splitext(filename)
    cap = ""
    if request.form.get('caption') != 'none':
        cap = request.form.get('caption')
    print(filename, fname, ext)
    print(filename, fname, ext)
    selfUser.post(filename, cap)
    selfUser.update()
    return redirect(url_for('home'))


@app.route("/check", methods=['POST'])
def check():

    uerror = userdb.checkUsername(request.form['username'])
    eerror = userdb.checkEmail(request.form['email'])
    perror = userdb.checkPhone(int(request.form['phone_no']))
    print(request.form['phone_no'], type(int(request.form['phone_no'])))
    print(uerror, eerror, perror)
    if userdb.getInfo(request.form['username']) or uerror == False or eerror == False or perror == False:
        return render_template("register.html", error=True, uerror=uerror, eerror=eerror, perror=perror)
    else:
        file = request.files['input_file']
        filename = photos.save(file)
        pdb = db_connection.Picturesdb()
        pdb.insert_into(filename)
        id = pdb.get_picture_id(filename)[0][0]
        userdb.insertInto([request.form['username'], request.form['email'], request.form['name'],
                           request.form['phone_no'], request.form['dob'], id, request.form['gender'], "",
                           request.form['bio'], 0, request.form['password'], request.form['city'], "",
                           request.form['link']])
        return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    if loginCheck(request.form['username'], request.form['password']):
        return redirect(url_for('home'))
    else:
        return render_template("login.html", error=True)


@app.route('/follow/<username>')
def follow(username):
        selfUser.follow(username)
        selfUser.update()
        return redirect(url_for('profile', username=username))


@app.route('/unfollow/<username>')
def unfollow(username):
        selfUser.unfollow(username)
        selfUser.update()
        return redirect(url_for('profile', username=username))


@app.route('/like/<int:post_id>')
def like(post_id):
    selfUser.like(post_id)
    return redirect(url_for('home'))

if __name__ == "__main__":
    thread = threading.Thread(target=app.run)
    thread.daemon = True
    thread.start()
    #app.run(debug=True)

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow,self).__init__(*args, **kwargs)
        self.setWindowTitle("InstaShare")
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://127.0.0.1:5000/"))
        self.setCentralWidget(self.browser)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
