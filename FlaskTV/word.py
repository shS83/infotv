"""Word import using the shared Office converter."""

from FlaskTV.office import convert_pages, image_html


MAX_PAGES = 100


def convert_word_pages(source, work_dir):
    return convert_pages(source, work_dir, extensions=('.doc', '.docx'),
                         document_entry='word/document.xml', pdf_filter='writer_pdf_Export',
                         image_prefix='page', max_pages=MAX_PAGES, error_prefix='doc')


def word_page_html(image_path, title):
    return image_html(image_path, title, 'infotv-word-page')
