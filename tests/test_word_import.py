from unittest.mock import patch
from zipfile import ZipFile

import test_powerpoint_import as powerpoint_tests
from FlaskTV.office import OfficeImportError
from FlaskTV.word import convert_word_pages, word_page_html


class WordConversionTests(powerpoint_tests.ConversionTests):
    extension = 'docx'
    document_entry = 'word/document.xml'
    converter = staticmethod(convert_word_pages)
    renderer = staticmethod(word_page_html)
    prefix = 'doc'
    image_prefix = 'page'
    limit_setting = 'FlaskTV.word.MAX_PAGES'
    pdf_filter = 'pdf:writer_pdf_Export'

    @patch('FlaskTV.office.shutil.which', return_value='/tool')
    def test_powerpoint_renamed_to_docx_is_rejected(self, _):
        with ZipFile(self.source, 'w') as archive:
            archive.writestr('ppt/presentation.xml', '<presentation/>')
        with self.assertRaisesRegex(OfficeImportError, 'doc_failed'):
            self.converter(self.source, self.root)

    @patch('FlaskTV.office.shutil.which', return_value='/tool')
    def test_invalid_legacy_doc_is_rejected(self, _):
        source = self.root / 'test.doc'
        source.write_bytes(b'not a Word document')
        with self.assertRaisesRegex(OfficeImportError, 'doc_failed'):
            self.converter(source, self.root)


class WordUploadTests(powerpoint_tests.UploadTests):
    prefix = 'doc'
    endpoint = '/design/import-word'
    field = 'word_file'
    extension = 'docx'
    legacy_extension = 'DOC'
    converter_patch = 'FlaskTV.routes.convert_word_pages'
    renderer_patch = 'FlaskTV.routes.word_page_html'
    page_label = 'page'
    button = 'Import a DOC/DOCX File'
    accept = '.doc,.docx'

    def test_powerpoint_extension_is_rejected(self):
        with patch(self.converter_patch) as convert:
            self.assertEqual(self.upload('presentation.pptx').status_code, 302)
            convert.assert_not_called()
