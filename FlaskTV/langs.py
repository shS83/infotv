from FlaskTV.forms import RegisterForm, LoginForm, DesignForm, ArrangeForm, RemoveForm, TimingForm, \
                          RegisterForm_fi, LoginForm_fi, DesignForm_fi, ArrangeForm_fi, RemoveForm_fi, TimingForm_fi, \
                          UAdminForm, UAdminForm_fi

LANGUAGES = ['en', 'fi']
DEFAULT_LANGUAGE = 'fi'
PREFIX = DEFAULT_LANGUAGE
FORMS = {
    'en': {
        'registerform': RegisterForm,
        'loginform': LoginForm,
        'designform': DesignForm,
        'arrangeform': ArrangeForm,
        'removeform': RemoveForm,
        'timingform': TimingForm,
        'uadminform': UAdminForm
    },
    'fi': {
        'registerform': RegisterForm_fi,
        'loginform': LoginForm_fi,
        'designform': DesignForm_fi,
        'arrangeform': ArrangeForm_fi,
        'removeform': RemoveForm_fi,
        'timingform': TimingForm_fi,
        'uadminform': UAdminForm_fi
    }
}

MESSAGES = {
    'en': {
        'rollback': 'Error, rolling back changes',
        'edit': 'Editing',
        'file_err': 'Error reading the file',
        'no_perm': 'No permission to edit',
        'emptyedit': 'Editor contents empty!',
        'name_required': 'Enter a new page description.',
        'io_err': 'File I/O Error!',
        'savesuccess': 'saved successfully!',
        'nomod': 'No modifications done.',
        'arranged': 'pages arranged.',
        'timesuccess': 'Success. Page timing modified.',
        'loginsuccess': 'Success! You are logged in as',
        'gen_err': 'Error:',
        'login_err': 'Username and password do not match! Please try again.',
        'commentclear': 'comments cleared!',
        'fileremoved': 'File removed',
        'logout': 'Logged out!',
        'nofilereq': 'No file in request',
        'nofilesel': 'No file selected',
        'invalid_import': 'Select an .html file. If the upload fails, reload the page and try again.',
        'ppt_invalid': 'Select a .ppt or .pptx file. Reload the page if the upload fails.',
        'doc_invalid': 'Select a .doc or .docx file. Reload the page if the upload fails.',
        'doc_unavailable': 'Word import requires LibreOffice Writer and Poppler (pdftoppm) on the server.',
        'doc_failed': 'The document could not be imported. Check that it opens in Word and is not password-protected.',
        'doc_timeout': 'The document took too long to convert. Try a smaller document.',
        'doc_too_large': 'The maximum Word file size is 50 MB.',
        'doc_too_many': 'A document can contain at most 100 pages. Split it into smaller files.',
        'doc_success': 'Imported {count} pages. Enable and order them on the Arrange page. Default display time is 10 seconds per page.',
        'ppt_unavailable': 'PowerPoint import requires LibreOffice Impress and Poppler (pdftoppm) on the server.',
        'ppt_failed': 'The presentation could not be imported. Check that it opens in PowerPoint and is not password-protected.',
        'ppt_timeout': 'The presentation took too long to convert. Try a smaller presentation.',
        'ppt_too_large': 'The maximum PowerPoint file size is 50 MB.',
        'ppt_too_many': 'A presentation can contain at most 100 slides. Split it into smaller files.',
        'ppt_success': 'Imported {count} slides. Enable and order them on the Arrange page. Default display time is 10 seconds per slide.',
        'file_exists': 'already exists.',
        'send_success': 'uploaded successfully.',
        'userdelete': 'User deleted successfully.',
        'passchange': 'User\'s password has been changed.',
        'noconfirm': 'No confirmation received.',
        'noadmin': 'Administration privilege needed.'
    },
    'fi': {
        'rollback': 'Virhe, perutaan muutokset.',
        'edit': 'Muokataan sivua',
        'file_err': 'Virhe luettaessa tiedostoa',
        'no_perm': 'Ei oikeuksia muokata tiedostoa',
        'emptyedit': 'Editorin sisältö tyhjä!',
        'name_required': 'Anna sivulle uusi kuvaus.',
        'io_err': 'Tiedoston I/O virhe!',
        'savesuccess': 'tallennettiin onnistuneesti!',
        'nomod': 'Ei muokkauksia.',
        'arranged': 'sivua järjestelty.',
        'timesuccess': 'Onnistui. Sivujen ajastus muutettu.',
        'loginsuccess': 'Onnistui! Olet kirjautuneena käyttäjänä',
        'gen_err': 'Virhe:',
        'login_err': 'Käyttäjänimi ja salasana eivät täsmää! Ole hyvä ja yritä uudelleen.',
        'commentclear': 'kommenttia tyhjennetty!',
        'fileremoved': 'Tiedosto poistettu',
        'logout': 'Kirjauduit ulos!',
        'nofilereq': 'Ei tiedostoa pyynnössä',
        'nofilesel': 'Ei tiedostoa valittu',
        'invalid_import': 'Valitse .html-tiedosto. Jos lähetys epäonnistuu, päivitä sivu ja yritä uudelleen.',
        'ppt_invalid': 'Valitse .ppt- tai .pptx-tiedosto. Päivitä sivu, jos lähetys epäonnistuu.',
        'doc_invalid': 'Valitse .doc- tai .docx-tiedosto. Päivitä sivu, jos lähetys epäonnistuu.',
        'doc_unavailable': 'Word-tuonti vaatii palvelimelle LibreOffice Writerin ja Popplerin (pdftoppm).',
        'doc_failed': 'Asiakirjan tuonti epäonnistui. Tarkista, että tiedosto avautuu Wordissa eikä ole suojattu salasanalla.',
        'doc_timeout': 'Asiakirjan muuntaminen kesti liian kauan. Kokeile pienempää asiakirjaa.',
        'doc_too_large': 'Word-tiedoston enimmäiskoko on 50 Mt.',
        'doc_too_many': 'Asiakirjassa voi olla enintään 100 sivua. Jaa asiakirja pienempiin tiedostoihin.',
        'doc_success': 'Tuotiin {count} sivua. Ota sivut käyttöön ja järjestä ne Järjestely-sivulla. Oletusnäyttöaika on 10 sekuntia sivulle.',
        'ppt_unavailable': 'PowerPoint-tuonti vaatii palvelimelle LibreOffice Impressin ja Popplerin (pdftoppm).',
        'ppt_failed': 'Esityksen tuonti epäonnistui. Tarkista, että tiedosto avautuu PowerPointissa eikä ole suojattu salasanalla.',
        'ppt_timeout': 'Esityksen muuntaminen kesti liian kauan. Kokeile pienempää esitystä.',
        'ppt_too_large': 'PowerPoint-tiedoston enimmäiskoko on 50 Mt.',
        'ppt_too_many': 'Esityksessä voi olla enintään 100 diaa. Jaa esitys pienempiin tiedostoihin.',
        'ppt_success': 'Tuotiin {count} diaa. Ota diat käyttöön ja järjestä ne Järjestely-sivulla. Oletusnäyttöaika on 10 sekuntia dialle.',
        'file_exists': 'on jo olemassa.',
        'send_success': 'lähetettiin onnistuneesti.',
        'userdelete': 'Käyttäjä poistettiin onnistuneesti.',
        'passchange': 'Käyttäjän salasana vaihdettu.',
        'noconfirm': 'Vahvistusta ei saatu.',
        'noadmin': 'Ylläpitäjän tunnus vaadittu.'
    }
}

ACTIONS = {
    'en': {
        'Enable': 'Enable',
        'Disable': 'Disable',
        'Timing change': 'Timing change',
        'Arrangement change': 'Arrangement change',
        'Page added': 'Page added',
        'Delete': 'Delete',
        'Rename': 'Rename',
        'Upload': 'Upload',
        'Page modified': 'Page modified'
    },
    'fi': {
        'Enable': 'Otettu käyttöön',
        'Disable': 'Poistettu käytöstä',
        'Timing change': 'Ajoituksen muutos',
        'Arrangement change': 'Järjestyksen muutos',
        'Page added': 'Sivu lisätty',
        'Delete': 'Poistettu',
        'Rename': 'Nimetty uudelleen',
        'Upload': 'Lähetetty',
        'Page modified': 'Sivu muokattu'
    }
}

COMMENTS = {
    'en': {
        'rename': 'Page renamed to',
        'edit': 'Page was edited',
        'newpage': 'New page'
    },
    'fi': {
        'rename': 'Sivun nimeksi vaihdettu',
        'edit': 'Sivua muokattiin',
        'newpage': 'Uusi sivu'
    }
}
