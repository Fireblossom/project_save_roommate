#encoding: utf-8

from flask import Flask, render_template, request, redirect, url_for, session
import config
from models import User, Contribute, Answer, Star
from exts import db
from decorators import login_required
from sqlalchemy import or_
import re

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)



@app.route('/')
def index():
    context = {
        'contributes': Contribute.query.order_by('-create_time').all()
    }
    return render_template('index.html', **context)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone, User.password ==
                                 password).first()
        if user:
            session['user_id'] = user.id
            # 如果想在31天内都不需要登录
            session.permanent = True
            if session['user_id'] == 1:
                return redirect(url_for('manage'))
            else:
                return redirect(url_for('index'))
        else:
            return u'手机号码或者密码错误，请确认好再登录'


@app.route('/regist/', methods=['GET', 'POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # 手机号码验证，如果被注册了就不能用了
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return u'该手机号码被注册，请更换手机'
        else:
            # password1 要和password2相等才可以
            if password1 != password2:
                return u'两次密码不相等，请核实后再填写'
            else:
                user = User(telephone=telephone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                # 如果注册成功，就让页面跳转到登录的页面
                return redirect(url_for('login'))

# 判断用户是否登录，只要我们从session中拿到数据就好了   注销函数
@app.route('/logout/')
def logout():
    # session.pop('user_id')
    # del session('user_id')
    session.clear()
    return redirect(url_for('login'))
@app.route('/manage/')
@login_required
def manage():
    user_id = session['user_id']
    if user_id != 1:
        return u'请用管理员账户登陆！'
    else:
        context = {
            'contributes': Contribute.query.order_by('-create_time').all()
        }
        return render_template('manage.html', **context)

@app.route('/user_list/')
@login_required
def user_list():
    user_id = session['user_id']
    if user_id != 1:
        return u'请用管理员账户登陆！'
    else:
        context = {
            'users': User.query.order_by('-id').all()
        }
        return render_template('user_list.html', **context)

@app.route('/contribute/', methods=['GET', 'POST'])
@login_required
def contribute():
    if request.method == 'GET':
        return render_template('contribute.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        poet = request.form.get('poet')
        dynasty = request.form.get('dynasty')
        contribute = Contribute(title=title, poet=poet, dynasty=dynasty, content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        contribute.author = user
        db.session.add(contribute)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/star/', methods=['GET'])
@login_required
def star():
    user_id = session['user_id']
    stars = Star.query.filter_by(author_id=user_id).all()
    contributes = list()
    for i in stars:
        contributes.append(Contribute.query.get(i.contribute_id))
    #print type(contributes)
    context = {
        'contributes': contributes
    }
    return render_template('star.html', **context)

@app.route('/detail/<contribute_id>/')
def detail(contribute_id):
    contribute_model = Contribute.query.filter(Contribute.id == contribute_id).first()
    logined = bool()
    stared = False
    try:
        user_id = session['user_id']
        logined = True
    except:
        logined = False
    if logined:
        stars = Star.query.filter_by(author_id=user_id).all()
        for i in stars:
            if i.contribute_id == int(contribute_id):
                stared = True
        #print stared
        if stared:
            star_text = u'取消收藏'
        else:
            star_text = u'立即收藏'
        stared = False
        return render_template('detail_login.html', contribute=contribute_model, star_text=star_text)
    else:
        return render_template('detail.html', contribute=contribute_model)

@app.route('/detail_manage/<contribute_id>/')
@login_required
def detail_manage(contribute_id):
    contribute_model = Contribute.query.filter(Contribute.id == contribute_id).first()
    return render_template('detail_manage.html', contribute=contribute_model)

@app.route('/answer_delete/<answer_id>/')
@login_required
def answer_delete(answer_id):
    if session['user_id'] != 1:
        return u'权限不足！'
    else:
        ans = Answer.query.filter(Answer.id == answer_id).first()
        id = ans.contribute_id#巨不优雅
        Answer.query.filter(Answer.id == answer_id).delete()
        db.session.commit()
        return redirect(url_for('detail_manage', contribute_id=id))

@app.route('/contribute_manage/<contribute_id>/', methods=['GET', 'POST'])
@login_required
def contribute_manage(contribute_id):
    if request.method == 'GET':
        contribute_model = Contribute.query.filter(Contribute.id == contribute_id).first()
        return render_template('contribute_manage.html', contribute=contribute_model)
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        poet = request.form.get('poet')
        dynasty = request.form.get('dynasty')
        contribute = Contribute.query.filter(Contribute.id == contribute_id).first()
        contribute.title = title
        contribute.poet = poet
        contribute.dynasty = dynasty
        contribute.content = content
        db.session.commit()
        return redirect(url_for('manage'))

@app.route('/user_manage/<user_id>/', methods=['GET', 'POST'])
@login_required
def user_manage(user_id):
    if request.method == 'GET':
        user_model = User.query.filter(User.id == user_id).first()
        return render_template('user_manage.html', user=user_model)
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.id == user_id).first()
        user.telephone = telephone
        user.username = username
        user.password = password
        db.session.commit()
        return redirect(url_for('user_list'))

@app.route('/user_delete/<user_id>/')
@login_required
def user_delete(user_id):
    if session['user_id'] != 1:
        return u'权限不足！'
    else:
        Star.query.filter(Star.author_id == user_id).delete()
        Answer.query.filter(Answer.author_id == user_id).delete()
        contribute = Contribute.query.filter(Contribute.author_id == user_id).all()
        for i in contribute:
            Answer.query.filter(Answer.contribute_id == i.id).delete()
        Contribute.query.filter(Contribute.author_id == user_id).delete()
        User.query.filter(User.id == user_id).delete()
        db.session.commit()#级联一直改不对，直接硬删吧，管他优雅不优雅
        return redirect(url_for('user_list'))


@app.route('/contribute_delete/<contribute_id>/')
@login_required
def contribute_delete(contribute_id):
    if session['user_id'] != 1:
        return u'权限不足！'
    else:
        Star.query.filter(Star.contribute_id == contribute_id).delete()
        Answer.query.filter(Answer.contribute_id == contribute_id).delete()
        Contribute.query.filter(Contribute.id == contribute_id).delete()
        db.session.commit()#同上
        return redirect(url_for('manage'))


@app.route('/add_answer/', methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    contribute_id = request.form.get('contribute_id')
    answer = Answer(content=content)
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()
    answer.author = user
    contribute = Contribute.query.filter(Contribute.id == contribute_id).first()
    answer.contribute = contribute
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail', contribute_id=contribute_id))

@app.route('/add_star/', methods=['POST'])
@login_required
def add_star():
    contribute_id = request.form.get('contribute_id')
    user_id = session['user_id']
    stars = Star.query.filter_by(author_id=user_id).all()
    stared = False
    for i in stars:
        if i.contribute_id == int(contribute_id):
            stared = True
            star = i
    if stared:
        db.session.delete(star)
    else:
        star = Star(contribute_id=contribute_id)
        star.author_id = user_id
        db.session.add(star)
    db.session.commit()
    stared = False
    return redirect(url_for('detail', contribute_id=contribute_id))

@app.route('/search/')
def search():
    q = request.args.get('q')
    # title, content
    # 或 查找方式（通过标题和内容来查找）
    contributes = Contribute.query.filter(or_(Contribute.title.contains(q), Contribute.content.contains(q), Contribute.poet.contains(q))).order_by('-create_time').all()
    # 与 查找（只能通过标题来查找）
    #contributes = Contribute.query.filter(Contribute.title.contains(q), Contribute.content.contains(q))
    return render_template('index.html', contributes=contributes)


# 钩子函数(注销)
@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    return {}

if __name__ == '__main__':
    app.run(debug=True)

