import unittest

from app import app, db, Movie, User, forge, initdb


class WatchlistTestCase(unittest.TestCase):

    def setUp(self):
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )

        db.create_all()
        user = User(name='Test', username='Test')
        user.set_password('123')
        movie = Movie(title='Test movie', year='2021')
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_app_exit(self):
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('页面走丢了 - 404', data)
        self.assertIn('回到主页', data)
        self.assertEqual(response.status_code, 404)

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test的观影清单', data)
        self.assertIn('Test movie', data)
        self.assertEqual(response.status_code, 200)

    def logon(self):
        self.client.post('/login', data=dict(
            username='Test',
            password='123'
        ), follow_redirects=True)

    def test_create_itme(self):
        self.logon()

        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2022'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('添加成功', data)
        self.assertIn('New Movie', data)

        response = self.client.post('/', data=dict(
            title='',
            year='2022'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('添加成功', data)
        self.assertIn('非法输入', data)

        response = self.client.post('/', data=dict(
            title='新电影',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('添加成功', data)
        self.assertIn('非法输入', data)

    def test_update_item(self):
        self.logon()

        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('编辑电影', data)
        self.assertIn('Test movie', data)
        self.assertIn('2021', data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='Test movie edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('更新成功', data)
        self.assertIn('Test movie edited', data)
        self.assertIn('2019', data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2012'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('更新成功', data)
        self.assertNotIn('2012', data)
        self.assertIn('非法输入', data)

    def test_delete_item(self):
        self.logon()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('删除成功', data)
        self.assertNotIn('Test movie edited', data)

    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('登出', data)
        self.assertNotIn('设置', data)
        self.assertNotIn('<form', data)
        self.assertNotIn('编辑', data)
        self.assertNotIn('删除', data)

    def test_login(self):
        response = self.client.post('/login', data=dict(
            username='Test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('登录成功', data)
        self.assertIn('登出', data)

        # response = self.client.post('/login', data=dict(
        #     username='Test',
        #     password='456'
        # ), follow_redirects=True)
        # data = response.get_data(as_text=True)
        # self.assertNotIn('登录成功', data)
        # self.assertNotIn('登出', data)
        # self.assertIn('用户名或密码错误', data)

        # response = self.client.post('/login', data=dict(
        #     username='',
        #     password='456'
        # ), follow_redirects=True)
        # data = response.get_data(as_text=True)
        # self.assertNotIn('登录成功', data)
        # self.assertNotIn('登出', data)
        # self.assertIn('非法输入', data)

    def test_logout(self):
        self.logon()
        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('再见', data)
        self.assertNotIn('登出', data)
        self.assertNotIn('<form', data)

    def test_settings(self):
        self.logon()
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('设置', data)
        self.assertIn('名字', data)

        response = self.client.post('/settings', data=dict(
            name='Alan Liang'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('更新成功', data)
        self.assertIn('Alan Liang', data)

        response = self.client.post('/settings', data=dict(
            name=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('更新成功', data)
        self.assertIn('非法输入', data)

    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('已建立模拟数据', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('数据库初始化完成', result.output)

    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(
            args=['admin', '--username', 'alan', '--password', '123'])
        self.assertIn('创建用户', result.output)
        self.assertIn('完成', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'alan')
        self.assertTrue(User.query.first().validate_password('123'))

    def test_admin_command_update(self):
        result = self.runner.invoke(
            args=['admin', '--username', 'peter', '--password', '456'])
        self.assertIn('更新用户', result.output)
        self.assertIn('完成', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'peter')
        self.assertTrue(User.query.first().validate_password('456'))


if __name__ == '__main__':
    unittest.main()
