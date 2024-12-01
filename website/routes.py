from reviews import app, db
from flask import render_template, request, url_for, redirect, flash
from sqlalchemy import text
from reviews import functionalities as fu
from datetime import timedelta
import re

@app.route('/')
def main():
    print("loading / page")
    cookie = request.cookies.get('sessionID')
    username = fu.get_user_from_cookie(cookie)
    return redirect(url_for('home', session=username))

@app.route('/home')
def home():
    print("loading home page")
    cookie = request.cookies.get('sessionID')
    username = fu.get_user_from_cookie(cookie)
    return render_template('home.html', session=username)

@app.route('/register', methods=['GET','POST'])
def register_page():
    print("loading registration page")
    if request.method == 'POST':
        email = request.form.get('EMail')
        username = request.form.get('Username')
        password = request.form.get('Password')
        fav_country = request.form.get('favcountry')

        if not re.match('.*@.*\..+', email): # check for loosely valid email format
            flash("invalid E-Mail format")
            return render_template('register.html', session=False)
        if email is None or isinstance(email, str) is False or len(email) < 5 or len(email) > 50:
            print("E-Mail error")
            flash("E-Mail error", category='warning')
            return render_template('register.html', session=False)
        if username is None or isinstance(username, str) is False or len(username) > 50:
            print("username error")
            flash("username error", category='warning')
            return render_template('register.html', session=False)
        if password is None or isinstance(password, str) is False or len(password) < 1 or len(password) > 50:
            print("password error")
            flash("password error", category='warning')
            return render_template('register.html', session=False)

        query = f"select username from users where username='{username}'"
        print(query)
        result = db.session.execute(text(query))
        user = result.fetchall()

        query = f"select email_address from users where email_address='{email}'"
        print(query)
        result = db.session.execute(text(query))
        mail = result.fetchall()

        if user:
            print("username already exists")
            flash("username already exists", category='warning')
            return render_template('register.html', session=False)
        elif mail:
            print("E-Mail already exists")
            flash("E-Mail already exists", category='warning')
            return render_template('register.html', session=False)

        query = f"insert into users (username, email_address, password, fav_country) values ('{username}', '{email}', '{password}', '{fav_country}')"
        print(query)
        result = db.session.execute(text(query))
        db.session.commit()

        query = f"select id from users where username='{username}'"
        result = db.session.execute(text(query))

        flash("Registration succesfull")
        return redirect(url_for('profile', session=username))

    cookie = request.cookies.get('sessionID')
    username = fu.get_user_from_cookie(cookie)
    return render_template('register.html', session=username)

@app.route('/login', methods=['GET','POST'])
def login():
    print("loading login page")
    cookie = request.cookies.get('sessionID')
    username = fu.get_user_from_cookie(cookie)

    if request.method == 'POST':
        username = request.form.get('Username')
        password = request.form.get('Password')

        if username is None or isinstance(username, str) is False or len(username) > 50:
            print("username error")
            flash("username error", category='warning')
            return render_template('login.html', session=False)
        if password is None or isinstance(password, str) is False or len(password) < 1 or len(password) > 50:
            print("password error")
            flash("password error", category='warning')
            return render_template('login.html', session=False)

        query = f"select username, id from users where username='{username}' and password='{password}'"
        print(query)
        result = db.session.execute(text(query))
        user = result.fetchall()

        if not user:
            print("wrong username + password combination")
            flash("wrong username + password combination", category='warning')
            return render_template('login.html', session=False)
        
        id = user[0][1]

        cookie = fu.create_cookie_session(id)

        flash("Login succesfull")
        response = redirect(url_for('profile', session=username))
        response.set_cookie("sessionID", cookie, max_age=timedelta(days=1))
        return response

    
    return render_template('login.html', session=username)

@app.route("/logout")
def session_logout():
    print("loading logout page")
    cookie = request.cookies.get('sessionID')
    id = fu.get_id_from_cookie(cookie)
    username = fu.get_user_from_cookie(cookie)
    if username:
        fu.delete_cookie_session(id)
        flash("logged out")
        response = redirect(url_for('home', session=False))
        response.set_cookie("sessionID", "", expires=0)
        return response

    flash("please log in")
    return redirect(url_for('login', session=username))

@app.route("/profile")
def profile():
    print("loading profile page")
    cookie = request.cookies.get('sessionID')
    username = fu.get_user_from_cookie(cookie)
    if username:
        query = f"select email_address, fav_country from users where username='{username}'"
        print(query)
        result = db.session.execute(text(query))
        data = result.fetchall()
        mail = data[0][0]
        fav_country = data[0][1]
        return render_template('profile.html', session=username, mail=mail, fav_country=fav_country)

    flash("please log in")
    return redirect(url_for('login', session=username))

@app.route("/reviews", methods=['GET','POST'])
def reviews():
    print("loading reviews page")
    cookie = request.cookies.get('sessionID')
    username = fu.get_user_from_cookie(cookie)
    if username:
        if request.method == 'POST':
            country = request.form.get('country')
            review = request.form.get('review')

            # response for the errors
            response = redirect(url_for('reviews', session=username))

            try:
                rating = int(request.form.get('rating'))
            except:
                print("rating was not a number")
                flash("rating should be number", category='warning')
                return response
            
            if country is None or isinstance(country, str) is False or len(country) < 1 or len(country) > 50:
                print("country error")
                flash("country error", category='warning')
                return response
            if review is None or isinstance(review, str) is False or len(review) < 1 or len(review) > 300:
                print("review error")
                flash("review error", category='warning')
                return response
            if rating is None or isinstance(rating, int) is False or rating > 100:
                print(rating)
                print(type(rating))
                print("rating error")
                flash("rating error (info: max rating is 100)", category='warning')
                return response
            
            #query = f"insert into reviews (country, review, username, rating) values ('{country}', '{review}', '{username}', '{rating}')"
            query = text(f"insert into reviews (country, review, username, rating) values (:country, :review, :username, :rating)")
            print(query)
            result = db.session.execute(query, {"country": country, "review": review, "username": username, "rating": rating})
            db.session.commit()
            flash("Review added")

        query = f"select country, review, username, rating from reviews"
        result = db.session.execute(text(query))
        items = result.fetchall()
        return render_template('reviews.html', session=username, reviews=items)

    flash("please log in")
    return redirect(url_for('login', session=username))

@app.route("/search", methods=['GET','POST'])
def search():
    print("loading search page")
    cookie = request.cookies.get('sessionID')
    username = fu.get_user_from_cookie(cookie)
    if username:
        items = [] # placeholder for lines without results
        if request.method == 'POST':
            country = request.form.get('country')

            # response for the error
            response = redirect(url_for('search', session=username))

            if country is None or len(country) < 1:
                print("country error")
                flash("country error", category='warning')
                return response
            
            # case insensitive partial string search
            query = f"select country, review, username, rating from reviews where LOWER(country) LIKE LOWER('%{country}%')"

            print(query)
            try:
                result = db.session.execute(text(query))
                items = result.fetchall()
            except Exception as exception:
                flash("Error: " + str(exception))
                return render_template('search.html', session=username, reviews=[])
            flash("Searched for " + country)

        return render_template('search.html', session=username, reviews=items)

    flash("please log in")
    return redirect(url_for('login', session=username))
