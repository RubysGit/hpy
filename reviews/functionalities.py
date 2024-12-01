from hashlib import sha256
from datetime import datetime
from sqlalchemy import text
from reviews import db

def create_cookie_session(id: int): # create cookie and save it
    print("creating cookie session")
    raw_cookie = str(datetime.now()) + str(id)
    cookie = sha256(raw_cookie.encode('utf-8')).hexdigest()
    query = f"insert into sessions (id, cookie) values ('{id}', '{cookie}') on duplicate key update id='{id}', cookie='{cookie}'"
    print(query)
    db.session.execute(text(query))
    db.session.commit()
    
    return cookie

def delete_cookie_session(id: int): # delete cookie from storage
    print("deleting cookie session")
    query = f"delete from sessions where id='{id}'"
    print(query)
    result = db.session.execute(text(query))
    db.session.commit()
    return

def get_user_from_cookie(cookie: str): # get username for specific cookie
    print("getting username from cookie")
    if cookie:
        id = get_id_from_cookie(cookie)
        query = f"select username from users where id='{id}'"
        print(query)
        result = db.session.execute(text(query))
        username = result.fetchall()
        if username:
            return username[0][0]
    return False # returns false on fail for easy condition on return (doubles as cookie confirmer)

def get_id_from_cookie(cookie: str): # get username for specific cookie
    print("getting id from cookie")
    if cookie:
        query = f"select id from sessions where cookie='{cookie}'"
        print(query)
        result = db.session.execute(text(query))
        id = result.fetchall()
        if id:
            return id[0][0]
    return False # returns false on fail for easy condition on return (doubles as cookie confirmer)
