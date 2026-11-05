import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from jinja2 import ChoiceLoader, FileSystemLoader
from sqlalchemy import create_engine, text

from FlaskTV import app, db
from FlaskTV.models import Comment, Page, User


class LogoTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name) / 'FlaskTV'
        self.pages = self.root / 'templates' / 'info_pages'
        self.pages.mkdir(parents=True)
        self.context = app.app_context()
        self.context.push()
        self.original_engine = db.engines[None]
        db.engines[None] = create_engine('sqlite://')
        db.create_all()
        db.session.add_all([
            User(username='logo-test', email_address='logo@example.com', password_hash='unused'),
            User(username='other', email_address='other@example.com', password_hash='unused'),
            User(username='admin', email_address='admin@example.com', password_hash='unused'),
        ])
        db.session.commit()
        self.loader_patch = patch.object(app, 'jinja_loader', ChoiceLoader([
            FileSystemLoader(str(self.root / 'templates')), app.jinja_loader,
        ]))
        self.loader_patch.start()
        app.jinja_env.cache.clear()
        self.root_patch = patch.object(app, 'root_path', str(self.root))
        self.root_patch.start()
        self.cwd = os.getcwd()
        os.chdir(self.temp.name)
        self.client = app.test_client()
        self.login(1)

    def tearDown(self):
        os.chdir(self.cwd)
        self.root_patch.stop()
        self.loader_patch.stop()
        app.jinja_env.cache.clear()
        db.session.remove()
        db.engines[None].dispose()
        db.engines[None] = self.original_engine
        self.context.pop()
        self.temp.cleanup()

    def login(self, user_id):
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user_id)
            session['_fresh'] = True
        # Flask-Login caches the user on the outer test application context.
        from flask import g
        g.pop('_login_user', None)

    def add_page(self, name='logo-test.html', **values):
        (self.pages / name).write_text('<p>Logo test content</p>')
        page = Page(name=name, file=name, time=10, owner=1, enabled=True, **values)
        db.session.add(page)
        db.session.commit()
        return page

    def token(self):
        html = self.client.get('/profile').get_data(as_text=True)
        return re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html).group(1)

    def test_legacy_database_upgrade_is_repeatable_and_preserves_pages(self):
        engine = create_engine('sqlite://')
        try:
            with engine.begin() as connection:
                connection.execute(text('CREATE TABLE page (id INTEGER PRIMARY KEY, name TEXT)'))
                connection.execute(text("INSERT INTO page VALUES (1, 'Existing page')"))
            ensure_page_logo_column(engine)
            ensure_page_logo_column(engine)
            with engine.begin() as connection:
                self.assertEqual(connection.execute(text(
                    'SELECT id, name, splash_enabled FROM page'
                )).one(), (1, 'Existing page', 1))
                connection.execute(text('UPDATE page SET splash_enabled = 0'))
            ensure_page_logo_column(engine)
            with engine.connect() as connection:
                self.assertEqual(connection.execute(text('SELECT splash_enabled FROM page')).scalar(), 0)
        finally:
            engine.dispose()

    def test_new_pages_default_to_visible_logo(self):
        self.assertTrue(self.add_page().splash_enabled)
        for language in ('fi', 'en'):
            self.client.set_cookie('lang', language)
            html = self.client.get('/design').get_data(as_text=True)
            self.assertRegex(html, r'<input checked[^>]*name="splash_enabled"')
            self.assertIn('Info-TV logo', html)

    def test_design_saves_and_reloads_both_logo_states(self):
        for visible in (False, True, False):
            data = dict(name='Test page', filename='saved.html', time='12',
                        editor_content='<p>Saved content</p>')
            if visible:
                data['splash_enabled'] = 'y'
            self.assertEqual(self.client.post('/design', data=data).status_code, 302)
            page = Page.query.filter_by(file='saved.html').one()
            self.assertEqual(page.splash_enabled, visible)
            html = self.client.get('/design?edit=saved.html').get_data(as_text=True)
            checkbox = re.search(r'<input[^>]*name="splash_enabled"[^>]*>', html).group()
            self.assertEqual('checked' in checkbox, visible)

    def test_profile_toggle_is_localized_and_changes_only_selected_page(self):
        page = self.add_page()
        other = self.add_page('second.html')
        token = self.token()
        for language, off, on in [('fi', 'Logo pois', 'Logo näkyviin'), ('en', 'Logo off', 'Logo on')]:
            self.client.set_cookie('lang', language)
            self.assertIn(off, self.client.get('/profile').get_data(as_text=True))
            response = self.client.post('/profile', data={'toggle_logo': page.id, 'csrf_token': token})
            self.assertEqual(response.status_code, 302)
            self.assertFalse(page.splash_enabled)
            self.assertTrue(other.splash_enabled)
            self.assertIn(on, self.client.get('/profile').get_data(as_text=True))
            self.client.post('/profile', data={'toggle_logo': page.id, 'csrf_token': token})
            self.assertTrue(page.splash_enabled)
        self.assertEqual(Comment.query.count(), 4)

    def test_profile_toggle_requires_csrf_and_owner_or_admin(self):
        page = self.add_page()
        self.assertEqual(self.client.post('/profile', data={'toggle_logo': page.id}).status_code, 400)
        self.login(2)
        token = self.token()
        self.assertEqual(self.client.post('/profile', data={
            'toggle_logo': page.id, 'csrf_token': token,
        }).status_code, 403)
        self.assertTrue(page.splash_enabled)
        self.login(3)
        self.assertIn('name="toggle_logo"', self.client.get('/profile').get_data(as_text=True))
        self.assertEqual(self.client.post('/profile', data={
            'toggle_logo': page.id, 'csrf_token': token,
        }).status_code, 302)
        self.assertFalse(page.splash_enabled)

    def test_view_preview_and_rotation_use_each_pages_logo_setting(self):
        self.add_page('hidden.html', splash_enabled=False)
        self.add_page('visible.html')
        for index, (filename, visible) in enumerate([('hidden.html', False), ('visible.html', True)]):
            html = self.client.get(f'/view?cur_idx={index}&stop=true').get_data(as_text=True)
            logo = re.search(r'<div id="infotv-logo"[^>]*>', html).group()
            self.assertEqual('hidden' not in logo, visible)
            payload = self.client.get(f'/view/content?cur_idx={index}').get_json()
            self.assertEqual(payload['splash_enabled'], visible)
            self.assertIn('Logo test content', payload['html'])
            preview = self.client.get(f'/preview?page={filename}').get_data(as_text=True)
            self.assertEqual('infotv-logo-2.png' in preview, visible)

    def test_arrangement_preserves_logo_settings_for_enabled_and_disabled_pages(self):
        self.add_page('hidden.html', splash_enabled=False)
        self.add_page('visible.html')
        for order in ('visible.html', 'hidden.html,visible.html'):
            self.assertEqual(self.client.post('/arrange', data={'arranged_items': order}).status_code, 302)
            self.assertFalse(Page.query.filter_by(file='hidden.html').one().splash_enabled)
            self.assertTrue(Page.query.filter_by(file='visible.html').one().splash_enabled)


if __name__ == '__main__':
    unittest.main()
