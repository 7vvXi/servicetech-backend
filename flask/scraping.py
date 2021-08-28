import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime
from flask import *
import ast
import os

app = Flask(__name__)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/api/v1/search', methods=['GET', 'POST'])
def index():
  if request.method == 'GET':
    word = request.args.get('key')
  else:
    word = request.form['key']

  if word == "ラーメン":  
    key = "ramen"
    u = "https://motto-jp.com/media/wp-content/uploads/2020/03/eyecatch-11.jpeg"
  elif word == "カレー":
    key = "curry"
    u = "https://japandaily.jp/wp-content/uploads/2015/08/curry.jpg"
  elif word == "デザート":
    key = "dessert"
    word = "チョコ"
    u = "https://www.silverkris.com/wp-content/uploads/2017/09/cafe-blanket.jpg"
  elif word == "ハンバーガー":
    key = "Burgers"
    u = "https://assets.epicurious.com/photos/57c5c6d9cf9e9ad43de2d96e/master/pass/the-ultimate-hamburger.jpg"
  elif word == "寿司" or word == "すし":
    key = "Sushi"
    u = "https://rimage.gnst.jp/livejapan.com/public/article/detail/a/00/00/a0000370/img/basic/a0000370_main.jpg?20201002142956&q=80&rw=750&rh=536"
  elif word == "ピザ":
    key = "Pizza"
    u = "https://pizza-olive.co.jp/wp-content/themes/olive/library/images/top-pizza.jpg"
  elif "丼" in word:
    key = "fast-food"
    u = "https://www.sirogohan.com/_files/recipe/images/gyuudon/gyuudon20082.JPG"
  else:
    key = word
    u = ""

  data = uberEats(key, u) + tabelog(word)
  print(data)
  return jsonify({'data':data})

@app.route('/api/v1/recommend', methods=['GET', 'POST'])
def recommend():
  import sys
  import pymysql.cursors
  connection = pymysql.connect(host='localhost',
                               user='root',
                               password='taberoi',
                               db='taberoi',
                               charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)

  with connection.cursor() as cursor:
    sql = "SELECT * FROM json_users ORDER BY RAND() LIMIT 1;"
    cursor.execute(sql)

    service = 2
    results = cursor.fetchall()
    col = ast.literal_eval(results[0]['col'])
    data = {'name':col['name'], 'price':col['price'], 'store':col['store'], 'deliv':col['deliv'], 'service':service, 'url':col['url']}

  connection.close()
  print(data)
  return jsonify({'data':data})

def uberEats(key, u):
  response = requests.get('https://www.ubereats.com/jp/category/tokyo-tokyo/' + key)
  soup = BeautifulSoup(response.text, 'html.parser')

  name = []
  money = []
  store = []
  s_money = []
  item = []
  i_money = []
  i_store = []
  d_money = []
  time = []

  for el in soup.find_all("p", text=re.compile("^(?!.*。).*$")):
    name.append(el.text)
  for el in soup.find_all(text=re.compile("^(?=.*((¥|\$)\d+))(?!.*\n).*$")):
    money.append(el) 
  for el in soup.find_all("span", text=re.compile("分")):
    time.append(el.text) 
  for i in range(len(money)):
    if "配送手数料" in money[i]:
      s_money.append(money[i])
      store.append(name[i])
      if i+1 < len(money):
        if "配送手数料" not in money[i+1]:
          i_store.append(name[i])
          d_money.append(money[i])
          i += 1
          i_money.append(money[i])
          item.append(name[i])

  data = []
  service = 1
  for i in range(len(i_money)):
    data.append({'name':item[i], 'price':i_money[i], 'store':i_store[i], 'deliv':d_money[i], 'service':service, 'url':u})

  return data

def tabelog(key):
  # モジュール読み込み
  import sys
  import pymysql.cursors
  # MySQLに接続する
  connection = pymysql.connect(host='localhost',
                               user='root',
                               password='taberoi',
                               db='taberoi',
                               charset='utf8',
                               # cursorclassを指定することで
                               # Select結果をtupleではなくdictionaryで受け取れる
                               cursorclass=pymysql.cursors.DictCursor)

  with connection.cursor() as cursor:
    sql = "SELECT * FROM json_users WHERE col->'$.\"name\"' LIKE '%"+key+"%';"
    cursor.execute(sql)

    data = []
    service = 2
    # Select結果を取り出す
    results = cursor.fetchall()
    for r in results:
      col = ast.literal_eval(r['col'])
      data.append({'name':col['name'], 'price':col['price'], 'store':col['store'], 'deliv':col['deliv'], 'service':service, 'url':col['url']})

    # MySQLから切断する
  connection.close()

  return data
  
if __name__ == '__main__':
  app.run()
