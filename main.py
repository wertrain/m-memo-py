# coding:utf-8
"""`main` is the top level module for your Bottle application."""
# import the Bottle framework
from bottle import Bottle, static_file, url, redirect, request, response
from bottle import jinja2_template, Jinja2Template
import short_url

import os
import random
import cgi
import datetime

from api import apis
from my.db import datastore
import common

Jinja2Template.defaults = {
    'title': u'みんなのメモ帳',
}

# Create the Bottle WSGI application.
bottle = Bottle()
# 別ファイルの API 部分をマージ
bottle.merge(apis)

def set_active_page(index):
    u""" 表示ページインデックスを設定 """
    Jinja2Template.defaults['active_page'] = index;

@bottle.route('/static/<filepath:path>')
@bottle.route('/timeline/static/<filepath:path>')
@bottle.route('/share/static/<filepath:path>')
@bottle.route('/login/static/<filepath:path>')
@bottle.route('/about/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')

@bottle.route('/')
def home():
    u""" HOME 画面を表示 """
    source_str = 'abcdefghijklmnopqrstuvwxyz'
    # 存在しない url を引くまで繰り返し
    while True:
        url = "".join([random.choice(source_str) for x in xrange(8)])
        if not datastore.exists_url(url):
            break
    redirect("/" + url)

@bottle.route('/<url>')
def home(url):
    u""" HOME 画面を表示 """
    # 変な URL だった場合はランダムURLにさせるため、ルートにリダイレクトする
    if not url.isalnum():
        redirect("/")
    # 現在の URL に対応するメモを取得する
    # ない場合は作成してしまう
    memo = datastore.get_memo_from_url(url)
    if memo == None:
        memo = datastore.save_memo('', url, url, '', os.environ['REMOTE_ADDR'])
    else:
        # 現在パスワードがかかっている場合
        if len(memo.password) != 0:
            session_id = request.get_cookie(common.cookie_index, secret=common.cookie_key)
            if session_id == None or not common.is_valid_session_id(memo.key().id(), session_id):
                redirect("/login/" + url)
    check_id = common.get_check_id(memo)
    set_active_page(0)
    return jinja2_template('html/home.html', {'url':url, 'text':memo.text, 'password': len(memo.password) != 0, 'check_id': check_id, 'public_flag': memo.public,'share':short_url.encode_url(memo.key().id())})

@bottle.route('/timeline/<page>')
def timeline(page):
    u""" 公開メモを表示 """
    MEMO_PER_PAGE = 5
    try:
        num = int(page, 10) - 1
        if num < 0:
            redirect("/timeline/1")
    except:
        redirect("/timeline/1")
    memos = []
    q = datastore.get_memo_all().filter('public =', True)
    q.order("-updated_at")
    for memo in q.run(offset=(num * MEMO_PER_PAGE), limit=MEMO_PER_PAGE):
        updated_at_jp = memo.updated_at + datetime.timedelta(hours = 9)
        memos.append({
          'text': common.convert_safe_text(memo.text), 
          'updated_at': updated_at_jp.strftime('%Y/%m/%d %H:%M:%S'),
          'share': short_url.encode_url(memo.key().id()),
        })

    # ページネーション用の設定
    pages = []
    start_page = num - 1
    while len(pages) <= 5:
        if start_page > 0:
            pages.append(start_page)
        start_page = start_page + 1
    previous_page = pages[0] - 1
    if previous_page <= 0:
        previous_page = 1
    next_page = pages.pop()
    
    set_active_page(1)
    return jinja2_template('html/timeline.html', {'memos':memos, 'pages':pages, 'current_page':num, 'previous_page':previous_page, 'next_page':next_page})

@bottle.route('/share/<url>')
def share(url):
    u""" メモ閲覧画面を表示 """
    if not url.isalnum():
        redirect("/")
    memo = datastore.get_memo_by_id(short_url.decode_url(url))
    updated_at_jp = memo.updated_at + datetime.timedelta(hours = 9)
    set_active_page(3)
    return jinja2_template('html/share.html', {'text':common.convert_safe_text(memo.text), 'updated_at': updated_at_jp.strftime('%Y/%m/%d %H:%M:%S')})

@bottle.route('/login/<url>')
def login(url):
    u""" ログイン画面を表示 """
    if not url.isalnum():
        redirect("/")
    memo = datastore.get_memo_from_url(url)
    if memo == None:
        redirect("/")
    if len(memo.password) == 0:
        redirect("/" + url)
    
    session_id = request.get_cookie(common.cookie_index, secret=common.cookie_key)
    if session_id != None and common.is_valid_session_id(memo.key().id(), session_id):
        redirect("/" + url)
    
    set_active_page(0)
    return jinja2_template('html/login.html', {'url':url})

@bottle.route('/about/service')
def about():
    u""" このサイトについてを表示 """
    set_active_page(2)
    return jinja2_template('html/about.html')

# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'

@bottle.route('/lock/<url>')
@bottle.post('/lock/<url>')
def unlock(url):
    u""" パスワードロック """
    if not url.isalnum():
        redirect("/")
    memo = datastore.get_memo_from_url(url)
    if memo == None:
        redirect("/")
    if len(memo.password) != 0:
        redirect("/" + url)
    password = request.forms.get('password')
    
    # いちいちログイン画面に飛ぶと煩わしいので
    # ログイン状態にしてしまう
    session_id = common.get_session_id(memo.key().id())
    response.set_cookie(common.cookie_index, session_id, secret=common.cookie_key, path="/")
    
    memo.password = password;
    memo.put()
    common.wait()
    redirect("/" + url)

@bottle.route('/unlock/<url>')
@bottle.post('/unlock/<url>')
def unlock(url):
    u""" パスワードロックを解除 """
    if not url.isalnum():
        redirect("/")
    memo = datastore.get_memo_from_url(url)
    if memo == None:
        redirect("/")
    if len(memo.password) == 0:
        redirect("/" + url)
    
    session_id = request.get_cookie(common.cookie_index, secret=common.cookie_key)
    if session_id == None or not common.is_valid_session_id(memo.key().id(), session_id):
        redirect("/login/" + url)
    response.delete_cookie(common.cookie_index)
    
    memo.password = ""
    memo.put()
    common.wait()
    redirect("/" + url)
    
@bottle.route('/change/<url>')
@bottle.post('/change/<url>')
def change(url):
    u""" URLを変更 """
    if not url.isalnum():
        redirect("/")
    memo = datastore.get_memo_from_url(url)
    if memo == None:
        redirect("/")
    newurl = request.forms.get('url');
    if not newurl.isalnum():
        redirect("/" + url)
    if datastore.exists_url(newurl):
        redirect("/" + url)
    memo.url = newurl
    memo.put()
    common.wait()
    redirect("/" + newurl)

@bottle.post('/authenticate/<url>')
def authenticate(url):
    if not url.isalnum():
        redirect("/")
    memo = datastore.get_memo_from_url(url)
    if memo == None:
        redirect("/" + url)
    if len(memo.password) == 0:
        redirect("/" + url)
    password = request.forms.get('password')
    if memo.password == password:
        session_id = common.get_session_id(memo.key().id())
        response.set_cookie(common.cookie_index, session_id, secret=common.cookie_key, path="/")
        next_url = "/" + url
    else:
        next_url = "/login/" + url
    common.wait()
    redirect(next_url)
    
@bottle.route('/system/delete_empty_memo')
def delete_empty_memo():
    now = datetime.datetime.now()
    # どうも空文字の場合はフィルタで取り出せないようなので、全検索としておく
    # http://stackoverflow.com/questions/598605/appengine-query-datastore-for-records-with-missing-value
    q = datastore.get_memo_all()#.filter('text =', '')
    q.order("-created_at")
    for memo in q.run():
        if len(memo.text) != 0:
            continue
        # まさにこのタスクが実行された瞬間にサービス利用者がいるとまずいので、
        # 今日書かれたメモは除外としておく
        if memo.created_at.year == now.year and memo.created_at.month == now.month and memo.created_at.day == now.day:
            continue
        memo.delete()
    return 'delete!'
