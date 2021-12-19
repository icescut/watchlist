from flask import Flask, url_for

app = Flask(__name__)


@app.route("/")
@app.route("/index")
@app.route("/home")
def hello():
    return "欢迎来到我的电影列表"


@app.route('/user/<name>')
def user_page(name):
    """测试path参数"""
    return f'用户：{name}'


@app.route('/test')
def test_url_for():
    """测试url_for"""
    print(url_for('hello'))
    print(url_for('user_page', name='alan'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for', num=2))
    return 'test page'
