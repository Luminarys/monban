import json
import os
import os.path
import hashlib
from glob import glob

config = {}
with open('config.json') as f:
        config = json.load(f)

from flask import Flask, send_file
from flask_basicauth import BasicAuth
app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = config['user']
app.config['BASIC_AUTH_PASSWORD'] = config['password']
dl_dir = config['directory']
basic_auth = BasicAuth(app)

ids = {}

@app.route("/dl/<string:file_id>")
def dl(file_id):
    if file_id in ids:
        path = ids[file_id]
        return send_file(path, conditional=True, as_attachment=True, attachment_filename=os.path.basename(path))
    else:
        return 'Are you looking for something?', 404

@app.route('/')
@basic_auth.required
def secret_view():
    files = [y for x in os.walk(dl_dir) for y in glob(os.path.join(x[0], '*'))]
    for f in files:
        fid = hashlib.sha1((f + config['password']).encode('utf8')).hexdigest()
        if not fid in ids:
            ids[fid] = f
    resp = ''
    sids = sorted(ids, key=ids.get)
    for fid in sids:
        resp += '<a href="dl/{}">{}</a><br>'.format(fid, ids[fid])
    return resp
