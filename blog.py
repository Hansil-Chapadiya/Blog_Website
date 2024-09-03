# Import Libraries
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os
import json
import math

# includeing Json file
config_file = './config.json'
with open(config_file, 'r') as c:
    params = json.load(c)["params"]

# run on local server
local_server = params['local_server']

# app name connect with templates folder
app = Flask(__name__, template_folder='templates')

# create secret key
app.secret_key = "secret-key"

# used for mail sending
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
)

# location save file
app.config['UPLOAD_FOLDER'] = params['upload_location']

# configure application with Mail
mail = Mail(app)

# differentiate local or production server
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

# add database with application
db = SQLAlchemy(app)

# Model of Post table


class Post(db.Model):
    '''
        sr_no,title,slug,content,date,img_file
    '''
    sr_no = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.Integer, nullable=False)
    img_file = db.Column(db.String(50), nullable=True)
    date = db.Column(db.String(12), nullable=True)

# Model of Contact table


class Contact(db.Model):
    '''
        sr_np,name,email,phone_no,msg,date
    '''
    sr_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    msg = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(12), nullable=True)

# routing the app "admin_login" page


@app.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
    if 'user' in session and session['user'] == params['admin_name']:
        posts_admin = Post.query.all()
        return render_template('dashboard.html', parameter=params, posts=posts_admin)
    if request.method == "POST":
        username = request.form.get('Username')
        password = request.form.get('Password')
        if username == params['admin_name'] and password == params['admin_password']:
            # set Session
            session['user'] = username
            posts_admin = Post.query.all()
            return render_template('dashboard.html', parameter=params, posts_=posts_admin)
    else:
        # rendering template to "Home" page
        return render_template('admin_login.html', parameter=params)
    return render_template('admin_login.html', parameter=params)
# routing the app "Home" page


@app.route("/")
def home():
    # Logic
    '''
        First
        prev = #
        next = page + 1
    '''
    '''
        Middle
        prev = page - 1
        next = next + 1
    '''
    '''
        Last
        prev = page - 1
        next = #
    '''
    post = Post.query.filter_by().all()
    print(post)
    last = math.ceil(len(post)/int(params['no_of_post']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1

    page = int(page)
    post = post[(page-1)*int(params['no_of_post']):(page-1) *
                int(params['no_of_post'])+int(params['no_of_post'])]
    if (page == 1):
        prev = "#"
        next = "/?page=" + str(page+1)
    elif (page == last):
        prev = "/?page=" + str(page-1)
        next = "#"
    else:
        prev = "/?page=" + str(page-1)
        next = "/?page=" + str(page+1)

    return render_template('index.html', parameter=params, posts=post, prev=prev, next=next)

# routing the app "About_us" page


@app.route("/about")
def about():
    # rendering template to "About_us" page
    return render_template('about.html', parameter=params)

# routing the app "Contact" page


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''Add Entry'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')

        entry = Contact(name=name, email=email, phone_no=phone,
                        msg=msg, date=datetime.now())  # entry in database
        db.session.add(entry)
        db.session.commit()
        my_mail = params['gmail_user']
        params['gmail_user'] = email
        mail.send_message('New Message From ' + name,
                          sender=my_mail,
                          recipients=[email],
                          body=msg + ":\n" + phone
                          )  # send mail after register

    # rendering template to "contact" page
    return render_template('contact.html', parameter=params)

# routing the app "Post" page


@app.route("/post")
def post():
    posts_db = Post.query.all()
    # rendering template to "Post" page
    return render_template('post.html', parameter=params, post=posts_db)
    # return jsonify("config.json")

# routing the app "1st Post" page


@app.route("/post/<string:slug_first_post>", methods=['GET', 'POST'])
def post_route_first(slug_first_post):
    post_first = Post.query.filter_by(slug=slug_first_post).first()
    # rendering template to "first_post" page
    return render_template('post.html', parameter=params, post=post_first)

# routing the app "Add/Edit" page


@app.route("/edit/<string:sr_no>", methods=['GET', 'POST'])
def edit(sr_no):
    if 'user' in session:
        if request.method == 'POST':
            '''
                sr_no,title,slug,content,date,img_file
            '''
            title_add_db = request.form.get('title')
            slug_add_db = request.form.get('slug')
            content_add_db = request.form.get('content')
            date_add_db = datetime.now()
            imgfile_add_db = request.form.get('img_file')

            if sr_no == '0':
                post = Post(title=title_add_db, slug=slug_add_db, content=content_add_db,
                            img_file=imgfile_add_db, date=date_add_db)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(sr_no=sr_no).first()
                post.title = title_add_db
                post.slug = slug_add_db
                post.content = content_add_db
                post.date = date_add_db
                post.img_file = imgfile_add_db
                db.session.commit()
                return redirect('/edit/' + sr_no)

    post = Post.query.filter_by(sr_no=sr_no).first()
    return render_template('edit.html', posts=post, parameter=params, sno=sr_no)


@app.route("/uploader", methods=["GET", "POST"])
def uploader():
    if 'user' in session and session['user'] == params['admin_name']:
        if request.method == "POST":
            f = request.files['file1']
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER']), secure_filename(f.filename))
            return "uploaded Successfully"


@app.route("/delete/<string:sr_no>", methods=['GET', 'POST'])
def delete(sr_no):
    if 'user' in session:
        post = Post.query.filter_by(sr_no=sr_no).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/admin_login")


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/admin_login')

# @app.route("/")
# def pagination():
    # #Logic
    # '''
    #     First
    #     prev = #
    #     next = page + 1
    # '''
    # '''
    #     Middle
    #     prev = page - 1
    #     next = next + 1
    # '''
    # '''
    #     Last
    #     prev = page - 1
    #     next = #
    # '''
    # post = Post.query.filter_by().all()
    # last = math.ceil(len(post)/int(params['no_of_post']))
    # page = request.args.get('page')
    # if(not str(page).isnumeric()):
    #     page = 1

    # page = int(page)
    # post = post[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]
    # if(page == 1):
    #     prev = "#"
    #     next = "/?page=" + str(page+1)
    # elif(page==last):
    #     prev = "/?page=" + str(page-1)
    #     next =  "#"
    # else:
    #     prev = "/?page=" + str(page-1)
    #     next = "/?page=" + str(page+1)

    # return render_template('index.html', parameter=params, posts=post, prev=prev, next=next)


if __name__ == '__main__':
    app.run(debug=True)
