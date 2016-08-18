# coding:utf-8
from bottle import Bottle, request, post, redirect
import json
from my.db import datastore
import os
import urllib
import common

apis = Bottle()

@apis.post('/private/api/update')
def update_memo():
    text = urllib.unquote(request.forms.get('text')).decode('utf-8')
    url = request.forms.get('url')
    if not url.isalnum():
        return 'False'
    memo = datastore.get_memo_from_url(url)
    if not common.check_id(memo, str(request.forms.get('api'))):
        return 'False'
    return str(datastore.update_memo_text(memo, text, url, os.environ['REMOTE_ADDR']))

@apis.post('/private/api/change')
def valid_url():
    url = request.forms.get('url')
    if not url.isalnum():
        return 'False'
    return str(not datastore.exists_url(url))
    
@apis.post('/private/api/public')
def update_public_flag():
    url = request.forms.get('url')
    flag = request.forms.get('flag') == 'true'
    if not url.isalnum():
        return 'False'
    memo = datastore.get_memo_from_url(url)
    if not common.check_id(memo, str(request.forms.get('api'))):
        return 'False'
    return str(datastore.update_public_flag(memo, flag, url, os.environ['REMOTE_ADDR']))