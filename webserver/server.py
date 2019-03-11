#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "ky2398"
DB_PASSWORD = "c5hah160"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

USER_ID = ['XX']
ENTRY = ['0']
PRO_ID = ['XX']
#NEW_O = [0]

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  # cursor = g.conn.execute("SELECT Product_ID,Product_name,Price FROM Product")
  # names = []
  # for result in cursor:
  #   names.append([result[0],result[1],result[2]])  # can also be accessed using result[0]
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)
  filename = 'static/back_img/P3.png'

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", img=filename)

# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  # cursor = g.conn.execute("SELECT Us_ID,Users_name,Tel,DateofBirth FROM Users")
  # info = []
  # for r in cursor:
  #   info.append([r[0],r[1],r[2],r[3]])
  # cursor.close()
  # context = dict(data = info)
  return render_template("anotherfile.html")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  uid = request.form['id']
  psd = request.form['pwd']
  name = request.form['name']
  tel = request.form['tel']
  birth = request.form['birth']
  #print name
  #avoid same uid
  result = g.conn.execute(text('SELECT Us_ID from Users'))
  uid_hist = []
  for r in result:
    uid_hist.append(str(r[0]))
  if uid in uid_hist:
    filename = 'static/back_img/P9.jpg'
    return render_template('error_uid.html',img=filename)
  else:
    cmd = 'INSERT INTO Users(Us_ID,PWD,Users_name,Tel,DateofBirth) VALUES (:Us_ID,:PWD,:Users_name,:Tel,:DateofBirth)';
    g.conn.execute(text(cmd), Us_ID=uid,PWD=psd,Users_name=name,Tel=tel,DateofBirth=birth);
  #return render_template('index.html')
    return redirect('/')

@app.route('/users',methods=['GET'])
def users():
  uid = request.args.get('id')
  psd = request.args.get('pwd')
  USER_ID[0] = uid #get USER_ID to manipulate other related tabels
  filename = 'static/back_img/P1.png'
  result = g.conn.execute(text('SELECT PWD FROM Users where Us_ID=:id1'),id1=uid)
  for r in result:
    correct = r[0]
  if correct== psd:
    print('correct login!',psd)
    print('database pwd',correct)
    return render_template('u.html',img=filename)
  else:
    print('wrong!')
    print('database pwd',correct)
    print('your pwd',psd)
    filename = 'static/back_img/P8.jpg'
    return render_template('error_pwd.html',img = filename)

#go back to your homepage
@app.route('/comeback')
def comeback():
  filename = 'static/back_img/P1.png'
  return render_template('u.html', img = filename)

@app.route('/u_info')
def u_info():
  #print uid
  cmd = 'SELECT Us_ID,Users_name,Tel,DateofBirth from Users where Us_ID=:id1'
  cursor = g.conn.execute(text(cmd), id1=USER_ID[0])
  info = []
  for r in cursor:
    x = dict()
    x['ID'] = r[0]
    x['name'] = r[1]
    x['telephone'] = r[2]
    x['birthday'] = r[3]
    info.append(x)
  #info = [('ID',cursor[0][0]),('name',cursor[0][1]),('telephone',cursor[0][2]),('birth',cursor[0][3])]
  cursor.close()
  return render_template('user_info.html',user=info)

@app.route('/deliver')
def deliver():
  cursor = g.conn.execute(text('SELECT * FROM Delivery'))
  info = []
  for r in cursor:
    x = dict()
    x['Company_ID'] = r[0]
    x['Company_Name'] = r[1]
    x['Company_Telephone'] = r[2]
    info.append(x)
  #context = dict(data=info)
  print('company:', info)
  cursor.close()
  return render_template('company.html', firm = info)

@app.route('/order_hist')
def order_hist():
  cmd = 'SELECT O.Orders_ID,D.Company_NAME,O.Address,O.Total,O.status \
  FROM Orders AS O, Delivery AS D\
  WHERE O.Company_ID=D.Company_ID AND O.Us_ID=:id1'
  cursor = g.conn.execute(text(cmd),id1=USER_ID[0])
  info = []
  for r in cursor:
    x = dict()
    x['OID'] = r[0]
    x['Cname'] = r[1]
    x['Addr'] = r[2]
    x['total'] = r[3]
    x['status'] = r[4]
    info.append(x)
  cursor.close()
  filename = 'static/back_img/P4.png'
  return render_template('order_history.html',hist=info,img=filename)

@app.route('/wish')
def wish():
  cmd = 'SELECT W.Product_ID,P.Product_name,P.price,B.type_name,W.Quantity  \
  FROM Wish AS W,Product AS P, Belong AS B\
  WHERE W.Product_ID=P.Product_ID AND P.Product_ID=B.Product_ID AND Us_ID=:id1'
  cursor = g.conn.execute(text(cmd),id1=USER_ID[0])
  info = []
  for r in cursor:
    x = dict()
    x['PID'] = r[0]
    x['Pname'] = r[1]
    x['price'] = r[2]
    x['Tname'] = r[3]
    x['q'] = r[4]
    info.append(x)
  cursor.close()
  filename = 'static/back_img/P7.png'
  return render_template('wishfile.html',wishlist=info,img=filename)


@app.route('/_create',methods=['POST'])
def _create():
  cid = request.form['id']
  addrs = request.form['addr']
  cmd = 'INSERT INTO Orders(Us_ID,Company_ID,Address,Total,status) \
  VALUES(:Us_ID,:Company_ID,:Address,:Total,:status)'
  g.conn.execute(text(cmd),Us_ID=USER_ID[0],Company_ID=cid,Address=addrs,Total=0.0,status='Adding')

  filename = 'static/back_img/P1.png'
  return render_template('u.html',img=filename)

@app.route('/place',methods=['POST'])
def place():
  # result = g.conn.execute(text('SELECT max(Orders_ID) from Orders Group BY Us_ID having Us_ID=:uid'),uid=USER_ID[0])
  # for r in result:
  #   oid = int(r[0])
  oid = request.form['id']
  cmd = 'UPDATE Orders SET status=\'Ordered\' WHERE Orders_ID=:oid1'
  g.conn.execute(text(cmd),oid1=oid)

  filename = 'static/back_img/P1.png'
  return render_template('u.html',img=filename)

@app.route('/new_order')
def new_order():
  result = g.conn.execute(text('SELECT max(Orders_ID) from Orders Group BY Us_ID having Us_ID=:uid'),uid=USER_ID[0])
  for r in result:
    oid = int(r[0])
  cmd = 'SELECT P1.Product_ID, P1.Product_name, P2.Piece_ID, P1.price, O.Total \
  FROM Product AS P1, Piece AS P2, Orders AS O \
  WHERE P1.Product_ID=P2.Product_ID AND P2.Orders_ID=O.Orders_ID \
  AND O.Orders_ID=:oid1'
  result = g.conn.execute(text(cmd),oid1=oid)
  info = []
  for r in result:
    x = dict()
    x['PID'] = r[0]
    x['Pname'] = r[1]
    x['PieceID'] = r[2]
    x['price'] = r[3]
    x['total'] = r[4]
    info.append(x)
  return render_template('neworderfile.html', newly=info)


@app.route('/users/d1')
def d1():
  ENTRY[0] = '1'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Food\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart1.html", depart_info=info)

@app.route('/_search', methods=['GET'])
def _search():
  pid = request.args.get('id')
  PRO_ID[0] = pid
  cmd = 'SELECT P1.Piece_ID, P.Product_name, P.price \
  FROM Piece AS P1, Product AS P \
  where P1.Product_ID=P.Product_ID AND P1.Orders_ID is NULL AND P.Product_ID=:id1'
  cursor = g.conn.execute(text(cmd),id1=pid)
  info = []
  for r in cursor:
    x = dict()
    x['Piece'] = r[0]
    x['PID'] = r[1]
    x['price'] = r[2]
    info.append(x)
  cursor.close()
  return render_template("show.html",piece_info=info)

@app.route('/review')
def review():
  cmd = 'SELECT R.Review_ID,U.Users_name,P.Product_name,R.Content,R.Review_date,R.Rate \
  FROM Users AS U, Review AS R, Product AS P\
  WHERE U.Us_ID=R.Us_ID AND P.Product_ID=R.Product_ID AND R.Product_ID=:pid1'
  cursor = g.conn.execute(text(cmd),pid1=PRO_ID[0])
  info = []
  for r in cursor:
    x=dict()
    x['RID'] = r[0]
    x['Uname'] = r[1]
    x['Pname'] = r[2]
    x['content'] = r[3]
    x['date'] = r[4]
    x['rate'] = r[5]
    info.append(x)
  cursor.close()
  return render_template('reviewfile.html',history=info)

@app.route('/addReview', methods=['POST'])
def addReview():
  _content = request.form['content']
  _rate = request.form['rate']
  cmd = 'INSERT INTO Review(Us_ID,Product_ID,Content,Review_date,Rate) \
  VALUES(:Us_ID,:Product_ID,:Content,:Review_date,:Rate)'
  g.conn.execute(text(cmd),\
    Us_ID=USER_ID[0],Product_ID=PRO_ID[0],Content=_content,\
    Review_date=datetime.date.today(),Rate=_rate)

  #update review page
  cmd = 'SELECT R.Review_ID,U.Users_name,P.Product_name,R.Content,R.Review_date,R.Rate \
  FROM Users AS U, Review AS R, Product AS P\
  WHERE U.Us_ID=R.Us_ID AND P.Product_ID=R.Product_ID AND R.Product_ID=:pid1'
  cursor = g.conn.execute(text(cmd),pid1=PRO_ID[0])
  info = []
  for r in cursor:
    x=dict()
    x['RID'] = r[0]
    x['Uname'] = r[1]
    x['Pname'] = r[2]
    x['content'] = r[3]
    x['date'] = r[4]
    x['rate'] = r[5]
    info.append(x)
  cursor.close()
  return render_template('reviewfile.html',history=info)

@app.route('/_order', methods=['POST'])
def _order():
  pid = request.form['id']
  result = g.conn.execute(text('SELECT max(Orders_ID) from Orders Group BY Us_ID having Us_ID=:uid'),uid=USER_ID[0])
  for r in result:
    oid = int(r[0])
  print('order_id:',oid)
  result = g.conn.execute(text('SELECT P1.price from Product AS P1,Piece AS P2 where P2.Product_ID=P1.Product_ID AND P1.Product_ID=:id1'),id1=PRO_ID[0])
  for r in result:
    price = float(r[0])
  print('price:',price)
  result = g.conn.execute(text('SELECT status from Orders where Orders_ID=:oid1'),oid1=oid)
  for r in result:
    _status = r[0]
  if _status=='Adding':
    cmd = 'UPDATE Orders SET Total=Total+:p1 where status=\'Adding\' AND Orders_ID=:oid1 AND Us_ID=:uid'
    g.conn.execute(text(cmd),p1=price,oid1=oid,uid=USER_ID[0])
    cmd = 'UPDATE Piece SET Orders_ID=:oid1 where Piece_ID=:pid1 AND Product_ID=:pid2'
    g.conn.execute(text(cmd),oid1=oid,pid1=pid,pid2=PRO_ID[0])
    
    #update showed information
    cmd = 'SELECT P1.Piece_ID, P.Product_name, P.price \
    FROM Piece AS P1, Product AS P \
    where P1.Product_ID=P.Product_ID AND P1.Orders_ID is NULL AND P.Product_ID=:id1'
    cursor = g.conn.execute(text(cmd),id1=PRO_ID[0])
    info = []
    for r in cursor:
      x = dict()
      x['Piece'] = r[0]
      x['PID'] = r[1]
      x['price'] = r[2]
      info.append(x)
    cursor.close()
    return render_template("show.html",piece_info=info)
  else:
    print(_status)
    filename = 'static/back_img/P10.jpg'
    return render_template('error_order.html',img=filename)
  #return redirect('/_order')

@app.route('/addWish', methods=['POST'])
def addWish():
  #uid = request.form['u_id']
  pid = request.form['p_id']
  num = request.form['quan']
  #print name
  cmd = 'INSERT INTO Wish(Us_ID,Product_ID,Quantity) VALUES (:Us_ID,:Product_ID,:Quantity)';
  g.conn.execute(text(cmd), Us_ID=USER_ID[0],Product_ID=pid,Quantity=num);
  return redirect('/users/d' + ENTRY[0])

@app.route('/users/d2')
def d2():
  ENTRY[0] = '2'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Wearings\' AND B.type_name=T.type_name \
         AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart2.html", depart_info=info)

@app.route('/users/d3')
def d3():
  ENTRY[0] = '3'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Kids\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart3.html", depart_info=info)

@app.route('/users/d4')
def d4():
  ENTRY[0] = '4'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Home\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart4.html", depart_info=info)

@app.route('/users/d5')
def d5():
  ENTRY[0] = '5'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Kitchen\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart5.html", depart_info=info)

@app.route('/users/d6')
def d6():
  ENTRY[0] = '6'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Sports\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart6.html", depart_info=info)

@app.route('/users/d7')
def d7():
  ENTRY[0] = '7'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Pet\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart7.html", depart_info=info)

@app.route('/users/d8')
def d8():
  ENTRY[0] = '8'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Books\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart8.html", depart_info=info)

@app.route('/users/d9')
def d9():
  ENTRY[0] = '9'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Beauty\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart9.html", depart_info=info)

@app.route('/users/d10')
def d10():
  ENTRY[0] = '10'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Health\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart10.html", depart_info=info)

@app.route('/users/d11')
def d11():
  ENTRY[0] = '11'
  cmd = 'SELECT T.type_name, T.description, P.Product_ID, P.Product_name, P.price \
         from Type AS T,Product AS P, Belong AS B \
         where T.type_name=\'Office\' AND B.type_name=T.type_name AND B.Product_ID=P.Product_ID'
  cursor = g.conn.execute(text(cmd))
  info = []
  for r in cursor:
    x = dict()
    x['Tname'] = r[0]
    x['des'] = r[1]
    x['PID'] = r[2]
    x['Pname'] = r[3]
    x['price'] = r[4]
    info.append(x)
  cursor.close()
  return render_template("depart11.html", depart_info=info)


@app.route('/login')
def login():
    #return render_template("Home.html")
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()