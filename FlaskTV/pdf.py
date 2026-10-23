"""PDF import using Poppler to render each page as an image."""

from pathlib import Path
import shutil

from FlaskTV.office import OfficeImportError, _run, image_html


PDFImportError = OfficeImportError
MAX_PAGES = 100


def convert_pdf_pages(source, work_dir):
    renderer = shutil.which('pdftoppm')
    if not renderer:
        raise PDFImportError('pdf_unavailable')

    source, work_dir = Path(source), Path(work_dir)
    with source.open('rb') as pdf_file:
        if b'%PDF-' not in pdf_file.read(1024):
            raise PDFImportError('pdf_failed')

    _run([renderer, '-png', '-scale-to', '1920', '-l', str(MAX_PAGES + 1),
          str(source), str(work_dir / 'page')], 'pdf')
    pages = sorted(work_dir.glob('page-*.png'), key=lambda path: int(path.stem.rsplit('-', 1)[1]))
    if not pages:
        raise PDFImportError('pdf_failed')
    if len(pages) > MAX_PAGES:
        raise PDFImportError('pdf_too_many')
    return pages


def pdf_page_html(image_path, title):
    return image_html(image_path, title, 'infotv-pdf-page')
