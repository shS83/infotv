from FlaskTV.forms import RegisterForm, LoginForm, DesignForm, ArrangeForm, RemoveForm, TimingForm, \
                          RegisterForm_fi, LoginForm_fi, DesignForm_fi, ArrangeForm_fi, RemoveForm_fi, TimingForm_fi, \
                          UAdminForm, UAdminForm_fi

LANGUAGES = ['en', 'fi']
PREFIX = 'en'
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
