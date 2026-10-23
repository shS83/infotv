from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError

from FlaskTV import app, db
from FlaskTV.models import Comment, Page, User
from FlaskTV.routes import do_pages_exist


class ArrangementTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pages = self.root / 'templates' / 'info_pages'
        self.pages.mkdir(parents=True)
        self.context = app.app_context()
        self.context.push()
        self.original_engine = db.engines[None]
        db.engines[None] = create_engine('sqlite://')
        db.create_all()
        db.session.add(User(username='arrange-test', email_address='arrange@example.com',
                            password_hash='unused'))
        db.session.commit()
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session['_user_id'] = '1'
            session['_fresh'] = True
        # Keep the real template loader while isolating the content directory.
        app.jinja_loader
        self.root_patch = patch.object(app, 'root_path', str(self.root))
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        db.session.remove()
        db.engines[None].dispose()
        db.engines[None] = self.original_engine
        self.context.pop()
        self.temp.cleanup()

    def add_page(self, filename, enabled=True, exists=True):
        if exists:
            (self.pages / filename).write_text('<p>Test page</p>')
        page = Page(name='Title ' + filename, file=filename, time=23, owner=1, enabled=enabled)
        db.session.add(page)
        db.session.commit()
        return page

    def snapshot(self):
        return [(p.id, p.name, p.file, p.time, p.owner, p.enabled)
                for p in Page.query.order_by(Page.id).all()]

    def save(self, names):
        return self.client.post('/arrange', data={'arranged_items': ','.join(names),
                                                 'comments': 'Updated order'})

    def test_all_pages_can_be_enabled_and_reordered_repeatedly(self):
        names = [f'page-{i:02}.html' for i in range(40)]
        for i, name in enumerate(names):
            if i < 30:
                self.add_page(name, enabled=i < 20)
            else:
                (self.pages / name).write_text('<p>New page</p>')
        original = {p.file: (p.name, p.time, p.owner) for p in Page.query.all()}
        for order in [names, list(reversed(names)), names[:3], names]:
            self.assertEqual(self.save(order).status_code, 302)
            actual = Page.query.filter_by(enabled=True).order_by(Page.id).all()
            self.assertEqual([p.file for p in actual], order)
            self.assertEqual(Page.query.count(), 40)
            for page in Page.query.all():
                expected = original.get(page.file, (page.file, 10, 1))
                self.assertEqual((page.name, page.time, page.owner), expected)
        self.assertEqual(Comment.query.count(), 4)

    def test_failure_after_deletion_restores_original_pages_and_comment(self):
        self.add_page('first.html')
        self.add_page('second.html', enabled=False)
        before = self.snapshot()

        def fail_insert(connection, cursor, statement, parameters, context, executemany):
            if statement.startswith('INSERT INTO page'):
                raise SQLAlchemyError('simulated insert failure')

        event.listen(db.engine, 'before_cursor_execute', fail_insert)
        try:
            with self.assertLogs(app.logger, level='ERROR') as logs:
                self.assertEqual(self.save(['second.html', 'first.html']).status_code, 302)
            self.assertIn('simulated insert failure', '\n'.join(logs.output))
        finally:
            event.remove(db.engine, 'before_cursor_execute', fail_insert)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(Comment.query.count(), 0)
        with self.client.session_transaction() as session:
            self.assertEqual(session['_flashes'][-1][0], 'danger')

    def test_commit_failure_restores_original_arrangement(self):
        self.add_page('first.html')
        self.add_page('second.html', enabled=False)
        before = self.snapshot()
        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError('commit failed')), \
                self.assertLogs(app.logger, level='ERROR'):
            self.assertEqual(self.save(['second.html']).status_code, 302)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(Comment.query.count(), 0)

    def test_missing_or_duplicate_selection_does_not_modify_database(self):
        self.add_page('first.html')
        before = self.snapshot()
        for names in [['missing.html'], ['first.html', 'first.html'], []]:
            self.assertEqual(self.save(names).status_code, 302)
            self.assertEqual(self.snapshot(), before)
            self.assertEqual(Comment.query.count(), 0)
        self.assertEqual(self.client.post('/arrange').status_code, 302)
        self.assertEqual(self.snapshot(), before)

    def test_cleanup_removes_consecutive_missing_files_without_rebuilding_survivors(self):
        self.add_page('missing-1.html', exists=False)
        self.add_page('missing-2.html', exists=False)
        self.add_page('present.html', enabled=False)
        survivor = self.snapshot()[-1]
        with app.test_request_context('/arrange'):
            self.assertTrue(do_pages_exist())
        self.assertEqual(self.snapshot(), [survivor])

    def test_cleanup_failure_preserves_all_rows(self):
        self.add_page('missing.html', exists=False)
        self.add_page('present.html')
        before = self.snapshot()
        with app.test_request_context('/arrange'), \
                patch.object(db.session, 'commit', side_effect=SQLAlchemyError('commit failed')), \
                self.assertLogs(app.logger, level='ERROR'):
            self.assertFalse(do_pages_exist())
        self.assertEqual(self.snapshot(), before)

    def test_both_languages_show_all_available_html_files(self):
        self.add_page('enabled.html')
        self.add_page('disabled.html', enabled=False)
        (self.pages / 'new.html').write_text('<p>New page</p>')
        (self.pages / 'notes.txt').write_text('Not a page')
        for language in ['fi', 'en']:
            self.client.set_cookie('lang', language)
            response = self.client.get('/arrange')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            for name in ['enabled.html', 'disabled.html', 'new.html']:
                self.assertIn(f'id="{name}"', html)
            self.assertNotIn('notes.txt', html)
            self.assertIn('/static/arrange.js', html)


if __name__ == '__main__':
    unittest.main()
