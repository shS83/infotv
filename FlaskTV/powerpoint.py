"""PowerPoint import using the shared Office converter."""

from FlaskTV.office import MAX_UPLOAD_BYTES, OfficeImportError, convert_pages, image_html


PowerPointImportError = OfficeImportError
MAX_SLIDES = 100


def convert_slides(source, work_dir):
    return convert_pages(source, work_dir, extensions=('.ppt', '.pptx'),
                         document_entry='ppt/presentation.xml', pdf_filter='impress_pdf_Export',
                         image_prefix='slide', max_pages=MAX_SLIDES, error_prefix='ppt')


def slide_html(image_path, title):
    return image_html(image_path, title, 'infotv-powerpoint-slide')
