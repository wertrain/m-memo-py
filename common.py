# coding:utf-8
import time
from datetime import datetime
import cgi
import StringIO
import re
import secret
import markdown
import bleach

from my.util import cipher

# Signed cookie 用シークレットキー
cookie_key = secret.COOKIE_KEY
# 何日間セッションを許可するか
expire_day = 2
# Signed cookie を書き込むインデックス
cookie_index = secret.COOKIE_INDEX
# 簡易チェック用キー
check_key = secret.CHECK_KEY

# ブラウザ依存なのか、即応答を返してしまうと
# Cookie や Datastore の値が反映されないままになっていしまう
# 本当は反映されたかを厳密に確認すべきだが、 
# Datastore 資源へのアクセス増加になってしまうので
# 良くないが、単にこの関数を使ってスリープとしておく
def wait():
    time.sleep(0.1)

# セッションの仕様
# ログイン対象のメモの ID と 現在時刻を , で連結して
# Signed Cookie として書き込んでおく
# ex. 6384039388774400,2015-06-12 09:07:05
# 認証の判定では、メモの ID が合っているかと
# 現在時刻が一定以下かを調べる
def get_session_id(memo_id):
    date = datetime.now()
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")
    return str(memo_id) + ',' + date_str

def is_valid_session_id(memo_id, session_id):
    pair = session_id.split(",")
    if len(pair) != 2:
        return False
    s_memo_id = pair[0]
    if s_memo_id != str(memo_id):
        return False
    s_date = pair[1]
    date = datetime.strptime(s_date, "%Y-%m-%d %H:%M:%S")
    diff = datetime.now() - date
    if diff.days >= expire_day:
        return False
    return True

# API を外部から呼び出させないために、適当な文字列を暗号化し、
# それを使用時には送ってもらうものとする
# 現在の使用では、生成される文字列はメモごとに固定であるのでセキュリティとしては低い
def get_check_id(memo):
    return cipher.encrypt(check_key, str(memo.key().id()))

def check_id(memo, id):
    return cipher.decrypt(check_key, id) == str(memo.key().id())

# Markdown 化と HTML のエスケープを行う
def convert_safe_text(text):
    # 色々やろうとしたけど、以下の方法をとった
    # 1. マークダウン化
    # 2. マークダウン化した文字列から改行関係のタグを削除
    # 3. 改行関係のタグを削除して、まだタグがあるか判定
    # 4. タグがあれば、マークダウンを意図して書かれたと判定、
    #    タグがなくなれば、マークダウンを意図して書かれていないと判定
    all_tag = re.compile(r'(<!--.*?-->|<[^>]*>)')
    br_tag = re.compile(r'(<br>|<br />|<p>|</p>)')
    converted = markdown.markdown(text, safe_mode=True)
    match = all_tag.search(br_tag.sub('', converted))
    if match:
        return converted
    else:
        return cgi.escape(text).replace('\n','<br />')