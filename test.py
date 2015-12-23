# coding=utf-8

from toy.web import Toy

app = Toy()

@app.route('/index')
def index():
    return 'hello , toy'


if __name__ == '__main__':
    app.run()
