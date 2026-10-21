"""Shared LibreOffice conversion and self-contained page rendering."""

import base64
from html import escape
import os
from pathlib import Path
import shutil
import signal
import subprocess
from zipfile import BadZipFile, ZipFile


MAX_UPLOAD_BYTES = 50 * 1024 * 1024
CONVERSION_TIMEOUT = 120


class OfficeImportError(Exception):
    """The message key is translated by the upload route."""


def _run(command, error_prefix):
    try:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              start_new_session=True) as process:
            try:
                process.communicate(timeout=CONVERSION_TIMEOUT)
            except subprocess.TimeoutExpired as error:
                # LibreOffice launches child processes; stop the whole conversion on timeout.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.communicate()
                raise OfficeImportError(f'{error_prefix}_timeout') from error
            if process.returncode:
                raise OfficeImportError(f'{error_prefix}_failed')
    except OSError as error:
        raise OfficeImportError(f'{error_prefix}_failed') from error


def convert_pages(source, work_dir, *, extensions, document_entry, pdf_filter,
                  image_prefix, max_pages, error_prefix):
    """Return PNG paths in page order. All work stays in the caller's temp directory."""
    office = shutil.which('libreoffice') or shutil.which('soffice')
    renderer = shutil.which('pdftoppm')
    if not office or not renderer:
        raise OfficeImportError(f'{error_prefix}_unavailable')

    source, work_dir = Path(source), Path(work_dir)
    if source.suffix.lower() == extensions[1]:
        try:
            with ZipFile(source) as archive:
                if document_entry not in archive.namelist():
                    raise OfficeImportError(f'{error_prefix}_failed')
        except BadZipFile as error:
            raise OfficeImportError(f'{error_prefix}_failed') from error
    elif source.suffix.lower() == extensions[0]:
        with source.open('rb') as handle:
            if handle.read(8) != bytes.fromhex('d0cf11e0a1b11ae1'):
                raise OfficeImportError(f'{error_prefix}_failed')
    else:
        raise OfficeImportError(f'{error_prefix}_invalid')

    # An isolated profile also allows conversions while desktop LibreOffice is open.
    profile = work_dir / 'office-profile'
    (profile / 'user').mkdir(parents=True)
    (profile / 'user' / 'registrymodifications.xcu').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<oor:items xmlns:oor="http://openoffice.org/2001/registry">'
        '<item oor:path="/org.openoffice.Office.Common/Security/Scripting">'
        '<prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop>'
        '</item></oor:items>', encoding='utf-8')
    _run([office, f'-env:UserInstallation={profile.as_uri()}', '--headless',
          '--convert-to', f'pdf:{pdf_filter}', '--outdir', str(work_dir), str(source)], error_prefix)
    pdf = work_dir / f'{source.stem}.pdf'
    # LibreOffice can return success even when it could not open the document.
    if not pdf.is_file() or not pdf.stat().st_size:
        raise OfficeImportError(f'{error_prefix}_failed')

    _run([renderer, '-png', '-scale-to', '1920', '-l', str(max_pages + 1),
          str(pdf), str(work_dir / image_prefix)], error_prefix)
    pages = sorted(work_dir.glob(f'{image_prefix}-*.png'), key=lambda path: int(path.stem.rsplit('-', 1)[1]))
    if not pages:
        raise OfficeImportError(f'{error_prefix}_failed')
    if len(pages) > max_pages:
        raise OfficeImportError(f'{error_prefix}_too_many')
    return pages


def image_html(image_path, title, css_class):
    """Embed the image so the existing page move/delete workflow needs no extra assets."""
    image = base64.b64encode(Path(image_path).read_bytes()).decode('ascii')
    return (
        f'<div class="{escape(css_class, quote=True)}" '
        'style="position:fixed;inset:0;background:#000;z-index:0;">'
        f'<img alt="{escape(title, quote=True)}" src="data:image/png;base64,{image}" '
        'style="display:block;width:100%;height:100%;object-fit:contain;">'
        '</div>\n'
    )
