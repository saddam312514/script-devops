from flask import Flask
app = Flask(__name__)
res_no = 0
import redis
from redis import Redis
# POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
# REDIS_CLIENT = redis.Redis(connection_pool=POOL)
REDIS_CLIENT = Redis(host='localhost', port=6379, db=0)
import traceback

def res_count():

    global res_no

    res_no=res_no+1

    return res_no

@app.route('/')
def hello_geek():
    res_no = res_count()

    if res_no%5==0:
        REDIS_CLIENT = Redis(host='192.168.1.0.99', port=6379, db=0)
        REDIS_CLIENT.rpush('QUEUE', 1)
        print("\n\n pass ..", res_no)

    msg = str(res_no)
    return '<h1>Hello RES ' +msg + '</h2>'


if __name__ == "__main__":
    app.run(debug=False)
