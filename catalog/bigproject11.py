#!/usr/bin/env python3
from flask import (
    Flask,
    flash,
    render_template,
    request,
    url_for,
    redirect,
    jsonify
    )

import sys

from sqlalchemy import(
    Column,
    ForeignKey,
    Integer,
    String
    )

from sqlalchemy.ext.declarative import declarative_base
from flask import make_response

from sqlalchemy.orm import relationship, backref

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from sqlalchemy import create_engine


from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import os
import random
import string
import httplib2
import json
import requests


app = Flask(__name__)

Base = declarative_base()


class Admin(Base):
    __tablename__ = "admin"
    admin_id = Column(Integer, primary_key=True)
    admin_mail = Column(String(100), nullable=False)


class Books(Base):
    __tablename__ = "books"
    books_id = Column(Integer, primary_key=True)
    books_name = Column(String(100), nullable=False)
    books_admin = Column(Integer, ForeignKey('admin.admin_id'))
    books_relation = relationship(Admin)

    @property
    def serialize(self):
        return {
            'id': self.books_id,
            'name': self.books_name

        }


class Items(Base):
    __tablename__ = "items"
    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(100), nullable=False)
    item_price = Column(Integer, nullable=False)
    item_publisher = Column(String(100), nullable=False)
    item_image = Column(String(1000), nullable=False)
    item_pages = Column(Integer, nullable=False)
    item_isbn = Column(Integer, nullable=False)
    books_id = Column(Integer, ForeignKey('books.books_id'))
    item_relation = relationship(
        Books,
        backref=backref("books", cascade="all,delete"))

    @property
    def serialize(self):
        return {
            'id': self.item_id,
            'name': self.item_name,
            'price': self.item_price,
            'publisher': self.item_publisher,
            'image': self.item_image,
            'pages': self.item_pages,
            'isbn': self.item_pages

        }

engine = create_engine('sqlite:///books.db')
Base.metadata.create_all(engine)

session = scoped_session(sessionmaker(bind=engine))


CLIENT_DATA = json.loads(open("client_secrets.json").read())
CLIENT_ID = CLIENT_DATA["web"]['client_id']


# This method is used to delete the book Category
@app.route('/deleteCat', methods=['GET', 'POST'])
def deleteCat():
    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("Invalid user")
        return redirect(url_for('home'))

    books = session.query(Books).filter_by(
        books_admin=admin.admin_id
        ).all()
    if books is None:
        flash('There is no categories')
        return redirect(url_for('home'))
    print ('ok\n'*5, books)
    if request.method == 'GET':
        return render_template('deletebookcat.html', books=books)
    elif 'POST':
        delete = request.form
        print('\n'*5)
        hasDelete = False
        for each in delete:
            hasDelete = True
            category = session.query(Books).filter_by(
                books_id=int(delete[each])).one_or_none()
            session.delete(category)
        session.commit()
        if hasDelete:
            flash('delete success')
        else:
            flash('You have not selected any category to delete')
    return redirect(url_for('home'))


@app.route('/read')
def read():
    books = session.query(Items).all()
    msg = ""
    for each in books:
        msg += str(each.item_name)
    return msg


@app.route('/home')
def home():
    items = session.query(Items).all()
    return render_template(
        'showbookitems.html', Items=items, hasRecent=True, category_id=None)


# Edit the book Category
@app.route('/edit')
def editCat():
    categories = session.query(Books).all()
    if len(categories) == 0:
        flash('There are no categories to edit')
    return render_template('editbookcat.html', categoriesList=categories)


@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Books).all()
    return jsonify(books=[c.serialize for c in categories])


@app.route('/books/JSON')
def itemsJSON():
    items = session.query(Items).all()
    return jsonify(books=[i.serialize for i in items])


# Edit the book category
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editBookscategory(category_id):
    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("Invalid user")
        return redirect(url_for('home'))
    books = session.query(Books).filter_by(
        books_id=category_id
        ).one_or_none()
    if books is None:
        flash('Category is not available to edit')
        return redirect(url_for('home'))
    login_admin_id = admin.admin_id
    admin_id = books.books_admin
    if login_admin_id != admin_id:
        flash('You cannot edit')
        return redirect(url_for('home'))

    if request.method == 'POST':
        category_name = request.form['category_name']
        books.books_name = category_name
        session.add(books)
        session.commit()
        flash('Successfully updated')
        return redirect(url_for('home'))
    else:
        books = session.query(Books).filter_by(
            books_id=category_id
            ).one_or_none()
        return render_template(
            'editbookcategory.html',
            books_name=books.books_name,
            id_category=category_id)


# It Create new book Category
@app.route('/category/new', methods=['GET', 'POST'])
def newbookcat():
    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('new_category.html')
    else:
        category_name = request.form['category_name']
        if category_name:
            admin = session.query(Admin).filter_by(
                admin_mail=login_session['email']
                ).one_or_none()
            if admin is None:
                return redirect(url_for('home'))
            admin_id = admin.admin_id
            new_books = Books(
                books_name=category_name,
                books_admin=admin_id
                )
            session.add(new_books)
            session.commit()
            flash('your Category is now added')
            return redirect(url_for('home'))
        else:
            flash('Category cannot add successfully')
            return redirect(url_for('home'))


@app.route('/category/<int:category_id>/items.json')
def one_category_json(category_id):
    catsingle = session.query(Items).filter_by(books_id=category_id).all()
    return jsonify(Catsingle=[each.serialize for each in catsingle])


# This method shows all the book items
@app.route('/category/items')
def showitems():
    if request.method == 'GET':
        category_list = session.query(Items).filter_by(books_id=1).all()
    return render_template('showbookitems.html', categories=category_list)


# This method gives the details of the book
@app.route(
    '/category/<int:category_id>/items/<int:itemid>',
    methods=['GET', 'POST']
    )
def bookitemdetails(category_id, itemid):
    if request.method == 'GET':
        item = session.query(Items).filter_by(
            books_id=category_id,
            item_id=itemid
            ).one_or_none()
        return render_template(
            'item_details.html',
            Bname=item.item_name,
            Bprice=item.item_price,
            Bpublisher=item.item_publisher,
            Bimage=item.item_image,
            Bpages=item.item_pages,
            Bisbn=item.item_isbn
            )


# Edit the book items
@app.route(
    '/category/<int:categoryid>/items/<int:itemid>/edit',
    methods=['GET', 'POST']
    )
def editbookitem(categoryid, itemid):
    if 'email' not in login_session:
        flash("Please login")
        return redirect(url_for('login'))

    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("Invalid user")
        return redirect(url_for('home'))

    categoryname = session.query(Books).filter_by(
        books_id=categoryid
        ).one_or_none()
    if not categoryname:
        flash('Category not found')
        return redirect(url_for('home'))

    item = session.query(Items).filter_by(
        item_id=itemid,
        books_id=categoryid
        ).one_or_none()
    if not item:
        flash('invalid item')
        return redirect(url_for('home'))

    login_admin_id = admin.admin_id
    admin_id = categoryname.books_admin

    if login_admin_id != admin_id:
        flash('your not correct person to edit')
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['Bname']
        image = request.form['Bimage']
        price = request.form['Bprice']
        publisher = request.form['Bpublisher']
        pages = request.form['Bpages']
        isbn = request.form['Bisbn']
        item = session.query(Items).filter_by(
            books_id=categoryid,
            item_id=itemid
            ).one_or_none()
        if item:
            item.item_name = name
            item.item_image = image
            item.item_price = price
            item.item_publisher = publisher
            item.item_pages = pages
            item.item_isbn = isbn
        else:
            flash('no items')
            return redirect(url_for('home'))
        session.add(item)
        session.commit()
        flash('updated success')
        return redirect(url_for('home'))
    else:
        edit = session.query(Items).filter_by(item_id=itemid).one_or_none()
        if edit:
            return render_template(
                'edit_item.html',
                Bname=edit.item_name,
                Bprice=edit.item_price,
                Bpublisher=edit.item_publisher,
                Bimage=edit.item_image,
                Bpages=edit.item_pages,
                Bisbn=edit.item_isbn,
                catid=categoryid,
                Bid=itemid)
        else:
            return 'no items'


# Shows the categories of book items
@app.route('/category/<int:category_id>/items')
def showcatitems(category_id):
    if request.method == 'GET':
        items = session.query(Items).filter_by(books_id=category_id).all()
        if len(items) == 0:
            flash('There is no items')
        return render_template(
            'showbookitems.html', Items=items, category_id=category_id)


# Add new item
@app.route('/category/<int:categoryid>/items/new', methods=['GET', 'POST'])
def newbookitem(categoryid):
    if 'email' not in login_session:
        flash("Please login.")
        return redirect(url_for('login'))

    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("Invalid user")
        return redirect(url_for('home'))

    categoryname = session.query(Books).filter_by(
        books_id=categoryid
        ).one_or_none()
    if not categoryname:
        flash('Category not found')
        return redirect(url_for('home'))

    login_admin_id = admin.admin_id
    admin_id = categoryname.books_admin
    if (login_admin_id != admin_id):
        flash('your not the correct person')
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('addbookitem.html', cat_id=categoryid)
    else:
        name = request.form['Bname']
        image = request.form['Bimage']
        price = request.form['Bprice']
        publisher = request.form['Bpublisher']
        pages = request.form['Bpages']
        isbn = request.form['Bisbn']
        sid = categoryid
        new_item = Items(
            item_name=name,
            item_price=price,
            item_publisher=publisher,
            item_image=image,
            item_isbn=isbn,
            item_pages=pages,
            books_id=sid
            )
        session.add(new_item)
        session.commit()
        flash('The item is added')
        return redirect(url_for('home'))


# deletes the book item
@app.route('/category/<int:categoryid>/items/<int:itemid>/delete')
def deletebookitem(categoryid, itemid):
    if 'email' not in login_session:
        flash("Please login")
        return redirect(url_for('login'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("Invalid user")
        return redirect(url_for('home'))

    categoryname = session.query(Books).filter_by(
        books_id=categoryid
        ).one_or_none()
    if not categoryname:
        flash('Category was not found')
        return redirect(url_for('home'))

    item = session.query(Items).filter_by(
        books_id=categoryid,
        item_id=itemid
        ).one_or_none()
    if not item:
        flash('invalid item')
        return redirect(url_for('home'))

    login_admin_id = admin.admin_id
    admin_id = categoryname.books_admin

    if login_admin_id != admin_id:
        flash('your not the correct person to delete')
        return redirect(url_for('home'))
    item = session.query(Items).filter_by(item_id=itemid).one_or_none()
    if item:
        name = item.item_name
        session.delete(item)
        session.commit()
        flash('Successfully deleted'+str(name))
        return redirect(url_for('home'))
    else:
        flash('item was not found')
        return redirect(url_for('home'))


# login routing
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# It helps the user to loggedin and display flash profile


# GConnect
@app.route('/gconnect', methods=['POST', 'GET'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    request.get_data()
    code = request.data.decode('utf-8')

# Obtain authorization of code

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("""Failed to upgrade the authorisation code"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check Whether the access token is valid  or not

    access_token = credentials.access_token
    myurl = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    header = httplib2.Http()
    result = json.loads(header.request(myurl, 'GET')[1].decode('utf-8'))

    # If there was an error in the access token info, then it should be abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user or not.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app or not.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for further use.

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'
            ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get's the user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # It add provider to login session

    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    admin_id = userID(login_session['email'])
    if not admin_id:
        admin_id = createNewUser(login_session)
    login_session['admin_id'] = admin_id
    flash("Successfull Login %s" % login_session['email'])
    return "Verified Successfully"


def createNewUser(login_session):
    email = login_session['email']
    newAdmin = Admin(admin_mail=email)
    session.add(newAdmin)
    session.commit()
    admin = session.query(Admin).filter_by(admin_mail=email).first()
    admin_Id = admin.admin_id
    return admin_Id


def userID(admin_mail):
    try:
        admin = session.query(Admin).filter_by(admin_mail=admin_mail).one()
        return admin.admin_id
    except Exception as e:
        print(e)
        return None


# Gdisconnect
@app.route('/gdisconnect')
def gdisconnect():
    # It will only disconnect a connected user.
    del login_session['email']
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected'
            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # It Reset the user's session.

        del login_session['access_token']
        del login_session['gplus_id']
        response = redirect(url_for('home'))
        response.headers['Content-Type'] = 'application/json'
        flash("successfully signed out", "success")
        return response
    else:

        # If given token is invalid, unable to revoke token
        response = make_response(json.dumps(
            ' It has failed to revoke token for user'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def logout():
    if 'email' in login_session:
        flash('you are logged out')
        return gdisconnect()
    flash('You have already logout')
    return redirect(url_for('login'))


@app.context_processor
def inject_all():
    category = session.query(Books).all()
    return dict(mycategories=category)

if __name__ == '__main__':
    app.secret_key = "sireesha"
    app.run(host="localhost", port=5000)
