# coding:utf-8
u"""
    Google App Engine Datastore ラッパー

    このモジュールは Google App Engine Datastore をラップして使いやすくしたものです。

    __author__ = 'T.Miyata'
    __version__ = '0.1'
"""
from datetime import datetime
from google.appengine.ext import db

class Memo(db.Model):
    u"""
        メモを表すデータクラス
    """
    text = db.TextProperty()
    url = db.StringProperty()
    password = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now_add=False)
    author = db.StringProperty()
    public = db.BooleanProperty(default=False)

def save_memo(text, url, newurl, password, author):
    u"""
        Datastore にメモを保存する
        @param text
        @param url
        @param newurl
        @param password
        @param author
    """
    memo = get_memo_from_url(url)
    if memo == None:
        memo = Memo()
    memo.text = text
    memo.url = newurl
    memo.password = password
    memo.author = author
    memo.updated_at = datetime.now()
    memo.put()
    return memo

def update_memo_text(memo, text, url, author):
    u"""
        Datastore のメモを更新する
        @param text
        @param url
        @param author
    """
    if memo == None:
        return False
    memo.text = text
    memo.author = author
    memo.updated_at = datetime.now()
    memo.put()
    return True

def update_public_flag(memo, flag, url, author):
    u"""
        Datastore のメモを更新する
        @param flag
        @param url
        @param author
    """
    if memo == None:
        return False
    memo.public = flag
    memo.author = author
    memo.updated_at = datetime.now()
    memo.put()
    return True

def get_memo_text(url):
    u"""
        Datastore からメモのテキストを取得する
        @param url 取得するメモの URL
    """
    memo = get_memo_from_url(url)
    if memo == None:
        return ""
    return memo.text

def get_memo_from_url(url):
    u"""
        Datastore からメモを取得する
        @param url 取得するメモの URL
    """
    q = db.Query(Memo).filter('url =', url)
    return q.get()

def get_memo_by_id(id):
    u"""
        Datastore からメモのテキストを取得する
        @param url 取得するメモの URL
    """
    return Memo.get_by_id(id)

def remove_memo_from_url(url):
    u"""
        Datastore からメモを削除する
        @param url 削除するメモの URL
    """
    memo = get_memo_from_url(url)
    if not memo == None:
        memo.delete()

def exists_url(url):
    u"""
        指定の url のメモが存在するかチェックする
        @param url チェックする URL
    """
    return not get_memo_from_url(url) == None

def get_memo_all():
    return Memo.all()

def remove_memo_all():
    for memo in Memo.all():
        memo.delete()
