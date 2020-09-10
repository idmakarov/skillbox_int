import pickle
import time
from datetime import datetime

from flask import Flask, request, abort

app = Flask(__name__)
db = []
dump_file = 'db.pickle'


@app.route('/')
def hello_world():
    title = '<title>"This is my site!"</title>'
    head = '<head><h1>"Praise the sun!"</h1></head>'
    body = '<body>\
        <a href="https://www.yandex.ru">Стартовая страница Яндекса</a>\
        <br><a href="/status">Статус</a>\
        <br><a href="/send">Отсылка</a>\
        <br><a href="/messages">Получение</a>\
        </body>'
    return title + head + body


@app.route('/status')
def status():
    dnow = datetime.now()
    users = set([x['name'] for x in db])
    user_count = len(users)
    message_count = len(db)

    return {
        'status': True,
        'name': 'Messenger',
        'time': dnow.strftime('%d.%m.%Y %H:%M:%S'),
        'user_number': user_count,
        'message_number': message_count
    }


@app.route('/send', methods=['POST'])
def send():
    data = request.json

    db.append({
        'id': len(db),
        'name': data['name'],
        'text': data['text'],
        'timestamp': time.time()
    })

    with open(dump_file, 'wb') as f:
        pickle.dump(db, f)

    return {'ok': True}


@app.route('/messages')
def messages():
    global db
    if not db:
        try:
            with open(dump_file, 'rb') as f:
                db = pickle.load(f)
        except FileNotFoundError:
            print('Dump file was not found!')

    if 'after_id' in request.args:
        after_id = int(request.args['after_id']) + 1
    else:
        after_id = 0

    max_limit = 100
    if 'limit' in request.args:
        limit = int(request.args['limit'])
        if limit > max_limit:
            abort(400, 'too big limit')
    else:
        limit = max_limit

    return {'messages': db[after_id:after_id+limit]}


app.run()
