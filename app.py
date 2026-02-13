from flask import Flask, request, redirect, render_template_string
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB = "blog.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        created TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        author TEXT,
        content TEXT,
        created TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

STYLE = """
<style>
body {
    background: #0f1115;
    color: #e6e6e6;
    font-family: system-ui, sans-serif;
    max-width: 800px;
    margin: auto;
    padding: 20px;
}
a { color: #7aa2ff; text-decoration: none; }
input, textarea, button {
    background: #1b1f27;
    color: #e6e6e6;
    border: 1px solid #333;
    padding: 8px;
    width: 100%;
    margin-top: 6px;
}
button {
    cursor: pointer;
}
.post {
    background: #151922;
    padding: 16px;
    margin: 12px 0;
    border-radius: 8px;
}
.comment {
    background: #1b1f27;
    padding: 10px;
    margin: 6px 0;
    border-radius: 6px;
}
small { color: #888; }
</style>
"""

@app.route("/")
def index():
    conn = sqlite3.connect(DB)
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()

    html = """
    <h1>暗色博客</h1>
    <a href="/new">✍ 写文章</a>
    {% for p in posts %}
    <div class="post">
        <h2><a href="/post/{{p[0]}}">{{p[1]}}</a></h2>
        <small>{{p[3]}}</small>
        <p>{{p[2][:200]}}...</p>
    </div>
    {% endfor %}
    """
    return STYLE + render_template_string(html, posts=posts)

@app.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        conn = sqlite3.connect(DB)
        conn.execute(
            "INSERT INTO posts(title,content,created) VALUES(?,?,?)",
            (title, content, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()
        conn.close()
        return redirect("/")

    html = """
    <h1>写文章</h1>
    <form method="post">
        <input name="title" placeholder="标题">
        <textarea name="content" rows="10" placeholder="内容"></textarea>
        <button>发布</button>
    </form>
    """
    return STYLE + html

@app.route("/post/<int:pid>", methods=["GET", "POST"])
def post(pid):
    conn = sqlite3.connect(DB)

    if request.method == "POST":
        author = request.form["author"]
        content = request.form["content"]
        conn.execute(
            "INSERT INTO comments(post_id,author,content,created) VALUES(?,?,?,?)",
            (pid, author, content, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()

    post = conn.execute("SELECT * FROM posts WHERE id=?", (pid,)).fetchone()
    comments = conn.execute(
        "SELECT * FROM comments WHERE post_id=? ORDER BY id DESC", (pid,)
    ).fetchall()
    conn.close()

    html = """
    <a href="/">← 返回</a>
    <div class="post">
        <h2>{{post[1]}}</h2>
        <small>{{post[3]}}</small>
        <p>{{post[2]}}</p>
    </div>

    <h3>评论</h3>
    <form method="post">
        <input name="author" placeholder="名字">
        <textarea name="content" rows="3" placeholder="评论"></textarea>
        <button>提交</button>
    </form>

    {% for c in comments %}
    <div class="comment">
        <b>{{c[2]}}</b> <small>{{c[4]}}</small>
        <p>{{c[3]}}</p>
    </div>
    {% endfor %}
    """
    return STYLE + render_template_string(html, post=post, comments=comments)

if __name__ == "__main__":
    app.run(debug=True)
