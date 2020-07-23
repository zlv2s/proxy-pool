from flask import Flask, jsonify, request
from mongo_db import MongoDB
import random

app = Flask(__name__)


@app.route('/one')
def get_one():
    proxies = MongoDB().get(1)
    result = [proxy['proxy'] for proxy in proxies]
    x = random.randint(0, MongoDB().get_count() - 1)
    return jsonify(dict(proxy=result[x]))


@app.route('/all')
def get_many():
    #  http://127.0.0.1:5000/many?count=2
    # args = flask.request.args  # 参数提交
    proxies = MongoDB().get(1)
    result = [proxy['proxy'] for proxy in proxies]
    print(result)
    print(MongoDB().get_count())
    # x = random.randint(1,MongoDB().get_count()-1)
    res_dict = {'result': result}
    return jsonify(res_dict)


@app.route('/delete')
def delete():
    args = request.args
    MongoDB().delete({'proxy': args['proxy']})
    return '删除成功：{}'.format(args)


def run():
    app.run()
