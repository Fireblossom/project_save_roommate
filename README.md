帮室友做的毕设（

flask+mysql

python2.7

win10

第一步建一个虚拟环境然后activate
`pip install virtualecv`
`virtualenv blahblah`
`cd blahblah\Script`
`activate`

第二步安装依赖
`pip install -r requirements.txt`

第三步设置数据库地址
修改`config.py`中
`SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/your_database_name'`

第四步迁移数据库三连
`python manage.py db init`    # 创建迁移的仓库
`Python manage.py db migrate`  # 创建迁移的脚本
`python manage.py db upgrade`  # 更新数据库

随后直接启动
`python manage.py runserver`

打开 http://127.0.0.1:5000 并完成整个毕设（雾
