from flask import Flask, url_for, render_template

app = Flask(__name__)


name = '小冰'
movies = [
    {'title': '放牛班的春天', 'year': 2004},
    {'title': '摩登时代', 'year': 1936},
    {'title': '城市之光', 'year': 1931},
    {'title': '疯狂动物城', 'year': 2016},
    {'title': '大话西游之大圣娶亲', 'year': 1995},
]


@app.route("/")
def index():
    return render_template('index.html', name=name, movies=movies)
