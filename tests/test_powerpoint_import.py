import base64
from io import BytesIO
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

from flask import g
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from FlaskTV import app, db
from FlaskTV.models import Comment, Page, User
from FlaskTV.powerpoint import PowerPointImportError, convert_slides, slide_html


PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1sAAAAASUVORK5CYII=')


class ConversionTests(unittest.TestCase):
    extension = 'pptx'
    document_entry = 'ppt/presentation.xml'
    converter = staticmethod(convert_slides)
    renderer = staticmethod(slide_html)
    prefix = 'ppt'
    image_prefix = 'slide'
    limit_setting = 'FlaskTV.powerpoint.MAX_SLIDES'
    pdf_filter = 'pdf:impress_pdf_Export'

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / f'test.{self.extension}'
        with ZipFile(self.source, 'w') as archive:
            archive.writestr(self.document_entry, '<document/>')

    def fake_command(self, command, **kwargs):
        self.assertTrue(kwargs['start_new_session'])
        if '--convert-to' in command:
            (self.root / 'test.pdf').write_bytes(b'%PDF-test')
        else:
            for number in [10, 2, 1]:
                (self.root / f'{self.image_prefix}-{number}.png').write_bytes(PNG)
        process = MagicMock()
        process.__enter__.return_value = process
        process.returncode = 0
        process.communicate.return_value = (b'', b'')
        return process

    @patch('FlaskTV.office.shutil.which', side_effect=lambda name: f'/usr/bin/{name}')
    def test_conversion_uses_isolated_profile_and_numeric_order(self, _):
        with patch('FlaskTV.office.subprocess.Popen', side_effect=self.fake_command) as run:
            slides = self.converter(self.source, self.root)
        self.assertEqual([p.name for p in slides], [f'{self.image_prefix}-{number}.png' for number in [1, 2, 10]])
        self.assertIn(self.pdf_filter, run.call_args_list[0].args[0])
        self.assertIn(f'-env:UserInstallation={(self.root / "office-profile").as_uri()}', run.call_args_list[0].args[0])

    def test_missing_dependencies(self):
        with patch('FlaskTV.office.shutil.which', return_value=None):
            with self.assertRaisesRegex(PowerPointImportError, f'{self.prefix}_unavailable'):
                self.converter(self.source, self.root)

    @patch('FlaskTV.office.shutil.which', return_value='/tool')
    def test_invalid_file(self, _):
        self.source.write_bytes(b'not a presentation')
        with self.assertRaisesRegex(PowerPointImportError, f'{self.prefix}_failed'):
            self.converter(self.source, self.root)

    @patch('FlaskTV.office.shutil.which', return_value='/tool')
    def test_timeout(self, _):
        with patch('FlaskTV.office.subprocess.Popen') as popen, \
                patch('FlaskTV.office.os.killpg') as kill:
            process = popen.return_value.__enter__.return_value
            process.communicate.side_effect = [subprocess.TimeoutExpired('office', 120), None]
            with self.assertRaisesRegex(PowerPointImportError, f'{self.prefix}_timeout'):
                self.converter(self.source, self.root)
            kill.assert_called_once()
            process.communicate.assert_any_call(timeout=120)

    @patch('FlaskTV.office.shutil.which', return_value='/tool')
    def test_success_exit_without_pdf_is_failure(self, _):
        with patch('FlaskTV.office.subprocess.Popen') as popen:
            process = popen.return_value.__enter__.return_value
            process.returncode = 0
            process.communicate.return_value = (b'', b'Error: source file could not be loaded')
            with self.assertLogs('FlaskTV.office', level='WARNING') as logs, \
                    self.assertRaisesRegex(PowerPointImportError, f'{self.prefix}_failed'):
                self.converter(self.source, self.root)
            self.assertIn('source file could not be loaded', logs.output[0])
            self.assertIn('missing_output=True', logs.output[0])

    @patch('FlaskTV.office.shutil.which', return_value='/tool')
    def test_converter_failure_logs_diagnostics(self, _):
        with patch('FlaskTV.office.subprocess.Popen') as popen:
            process = popen.return_value.__enter__.return_value
            process.returncode = 1
            process.communicate.return_value = (b'Conversion failed', b'Permission denied\xff')
            with self.assertLogs('FlaskTV.office', level='WARNING') as logs, \
                    self.assertRaisesRegex(PowerPointImportError, f'{self.prefix}_failed'):
                self.converter(self.source, self.root)
            self.assertIn('exit=1', logs.output[0])
            self.assertIn('Conversion failed', logs.output[0])
            self.assertIn('Permission denied', logs.output[0])

    @patch('FlaskTV.office.shutil.which', return_value='/tool')
    def test_slide_limit(self, _):
        with patch('FlaskTV.office.subprocess.Popen', side_effect=self.fake_command), \
                patch(self.limit_setting, 2):
            with self.assertRaisesRegex(PowerPointImportError, f'{self.prefix}_too_many'):
                self.converter(self.source, self.root)

    def test_self_contained_slide_fits_screen_and_escapes_title(self):
        image = self.root / 'slide.png'
        image.write_bytes(PNG)
        html = self.renderer(image, 'A "title" <test>')
        self.assertIn('data:image/png;base64,', html)
        self.assertIn('object-fit:contain', html)
        self.assertIn('z-index:0', html)
        self.assertIn('A &quot;title&quot; &lt;test&gt;', html)


class UploadTests(unittest.TestCase):
    prefix = 'ppt'
    endpoint = '/design/import-powerpoint'
    field = 'powerpoint_file'
    extension = 'pptx'
    legacy_extension = 'PPT'
    converter_patch = 'FlaskTV.routes.convert_slides'
    renderer_patch = 'FlaskTV.routes.slide_html'
    page_label = 'slide'
    button = 'Import a PPT/PPTX file'
    accept = '.ppt,.pptx'

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
        db.session.add(User(username='ppt-test', email_address='ppt@example.com', password_hash='unused'))
        db.session.commit()
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session['_user_id'] = '1'
            session['_fresh'] = True
        response = self.client.get('/design')
        self.assertEqual(response.status_code, 200)
        self.token = re.search(rf'id="{self.prefix}-import-csrf"[^>]*value="([^"]+)"', response.get_data(as_text=True)).group(1)
        self.root_patch = patch.object(app, 'root_path', str(self.root))
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        db.session.remove()
        db.engines[None].dispose()
        db.engines[None] = self.original_engine
        self.context.pop()
        self.temp.cleanup()

    def fake_conversion(self, source, work_dir):
        result = []
        for number in [1, 2]:
            image = work_dir / f'page-{number}.png'
            image.write_bytes(PNG)
            result.append(image)
        return result

    def upload(self, filename=None, token=None):
        if filename is None:
            filename = f'test.{self.extension}'
        return self.client.post(self.endpoint, data={
            'csrf_token': self.token if token is None else token,
            self.field: (BytesIO(b'presentation'), filename),
        }, content_type='multipart/form-data')

    def test_import_registers_ordered_disabled_owned_pages_and_can_repeat(self):
        with patch(self.converter_patch, side_effect=self.fake_conversion):
            for filename in [f'../../test.{self.extension}', f'test.{self.legacy_extension}']:
                response = self.upload(filename)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.location, '/design')
        pages = Page.query.order_by(Page.id).all()
        self.assertEqual(len(pages), 4)
        self.assertEqual(len(set(page.file for page in pages)), 4)
        for index, page in enumerate(pages):
            self.assertTrue(page.file.endswith(f'{self.page_label}-{index % 2 + 1:03d}.html'))
            self.assertEqual((page.owner, page.time, page.enabled), (1, 10, False))
            self.assertIn('data:image/png;base64,', (self.pages / page.file).read_text())
        self.assertEqual(Comment.query.count(), 4)

    def test_validation_and_csrf_prevent_conversion(self):
        with patch(self.converter_patch) as convert:
            for filename, token in [('test.html', self.token), ('', self.token), (f'test.{self.extension}', '')]:
                self.assertEqual(self.upload(filename, token).status_code, 302)
            convert.assert_not_called()
        self.assertEqual(Page.query.count(), 0)

    def test_file_size_limit(self):
        with patch('FlaskTV.routes.MAX_UPLOAD_BYTES', 3), patch(self.converter_patch) as convert:
            self.assertEqual(self.upload().status_code, 302)
            convert.assert_not_called()
        self.assertEqual(list(self.pages.iterdir()), [])

    def test_conversion_failure_does_not_leave_pages(self):
        with patch(self.converter_patch, side_effect=PowerPointImportError(f'{self.prefix}_failed')):
            self.assertEqual(self.upload().status_code, 302)
        self.assertEqual(Page.query.count(), 0)
        self.assertEqual(list(self.pages.iterdir()), [])

    def test_partial_file_failure_rolls_back_all_slides(self):
        with patch(self.converter_patch, side_effect=self.fake_conversion), \
                patch(self.renderer_patch, side_effect=['first slide', OSError('disk full')]), \
                patch.object(app.logger, 'exception'):
            self.assertEqual(self.upload().status_code, 302)
        self.assertEqual(Page.query.count(), 0)
        self.assertEqual(Comment.query.count(), 0)
        self.assertEqual(list(self.pages.iterdir()), [])

    def test_database_failure_cleans_up_files(self):
        with patch(self.converter_patch, side_effect=self.fake_conversion), \
                patch.object(db.session, 'commit', side_effect=SQLAlchemyError('test')), \
                patch.object(app.logger, 'exception'):
            self.assertEqual(self.upload().status_code, 302)
        self.assertEqual(Page.query.count(), 0)
        self.assertEqual(list(self.pages.iterdir()), [])

    def test_login_required(self):
        g.pop('_login_user', None)
        response = app.test_client().post(self.endpoint)
        self.assertEqual(response.status_code, 401)

    def test_both_languages_render_separate_import_forms(self):
        for lang in ['fi', 'en']:
            self.client.set_cookie('lang', lang)
            response = self.client.get('/design')
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(self.button, html)
            self.assertIn(f'accept="{self.accept}"', html)
            self.assertEqual(html.count('<form '), 4)
            self.assertEqual(html.count('</form>'), 4)


if __name__ == '__main__':
    unittest.main()
