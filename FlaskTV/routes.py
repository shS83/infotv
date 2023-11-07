from FlaskTV import app
from flask import render_template, redirect, url_for, flash, request, make_response
from FlaskTV.models import Page, User, Comment
from FlaskTV import db
from flask_login import login_user, logout_user, login_required, current_user
from FlaskTV import secure_filename
from FlaskTV import exc
import FlaskTV.langs as langs
import os


def do_pages_exist():

    # Query for Page Model, clear the old table if files do not exist and write a replacement

    pages = Page.query.all()
    path = os.path.join(os.getcwd(), 'FlaskTV', 'templates', 'info_pages')
    files = os.listdir(path)

    modified = False

    for page in pages:
        if page.file not in files:
            pages.remove(page)
            modified = True

    if modified:
        try:
            db.session.query(Page).delete()
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            flash(langs.MESSAGES[langs.PREFIX]['rollback'], category='danger')
            return False

        for page in pages:
            page_to_create = Page(name=page.name, file=page.file, time=page.time,
                                  owner=page.owner, enabled=page.enabled)
            db.session.add(page_to_create)

        db.session.commit()

    return True


def get_lang_prefix():
    lang_prefix = 'en'
    if request.cookies.get('lang') == 'fi':
        lang_prefix = 'fi'
    langs.PREFIX = lang_prefix
    return lang_prefix


def safe_local_redirect(ref_url):
    if ref_url:
        response = ref_url.rsplit('/', 1)[1]
        if response:
            new_ref = url_for(f'{response}_page')
        else:
            new_ref = url_for('home_page')
        return new_ref
    else:
        return False


@app.route('/set')
@app.route('/set/<theme>')
def set_theme(theme='blue'):
    safe_redirect = safe_local_redirect(request.referrer)
    if safe_redirect:
        style_file = os.path.join(os.getcwd(), 'FlaskTV', 'static', f'{theme}.css')
        if os.path.isfile(f'{style_file}'):
            res = make_response(redirect(safe_redirect))
            res.set_cookie('theme', theme)
        else:
            print('ERROR: Style not found. Running with default.')
            res = make_response(redirect(safe_redirect))
            res.set_cookie('theme', 'blue')
        return res
    else:
        return redirect(url_for('home_page'))


@app.route('/lang')
@app.route('/lang/<lang>')
def set_lang(lang='en'):
    safe_redirect = safe_local_redirect(request.referrer)
    if safe_redirect:
        if lang in langs.LANGUAGES:
            res = make_response(redirect(safe_redirect))
            res.set_cookie('lang', lang)
            langs.PREFIX = lang
            return res
        else:
            print('ERROR: Language not implemented. Defaulting to english.')
            res = make_response(redirect(safe_redirect))
            res.set_cookie('lang', 'en')
            langs.PREFIX = 'en'
            return res
    else:
        return redirect(url_for('home_page'))


@app.route('/')
@app.route('/home')
def home_page():
    get_lang_prefix()
    return render_template(f'{langs.PREFIX}/home.html')


@app.route('/red_theme')
def red_theme():
    return redirect(url_for('home_page'))


@app.route('/view', methods=['GET'])
def view_page():
    do_pages_exist()
    pages = Page.query.filter_by(enabled=1).all()
    if len(pages) > 0:
        args = request.args
        if args:
            cur_idx = int(args.get('cur_idx'))
        else:
            cur_idx = 0

        nextpage = cur_idx+1
        if nextpage >= len(pages):
            nextpage = 0
        payload = {'current': pages[cur_idx].file, 'next': pages[nextpage].file, 'time': pages[cur_idx].time}
        return render_template('view.html', page=payload, pages=pages, cur_idx=nextpage)
    else:
        return render_template('view_empty.html')


@app.route('/design', methods=['GET', 'POST'])
@login_required
def design_page():
    get_lang_prefix()
    designform = langs.FORMS[langs.PREFIX]['designform']()
    designform.time.data = 10
    args = request.args
    to_edit = args.get('edit')
    page_to_edit = False
    editpage_query = False

    if request.method == 'GET':
        if to_edit:
            file_to_edit = os.path.join('FlaskTV', 'templates', 'info_pages', to_edit)
            if os.path.isfile(file_to_edit):
                if to_edit in [usr_owned.file for usr_owned in current_user.modified_pages] \
                        or current_user.username == 'admin':
                    editpage_query = Page.query.filter_by(file=to_edit).first()
                    if editpage_query:
                        designform.time.data = editpage_query.time
                        designform.name.data = editpage_query.name
                        designform.filename.data = editpage_query.file
                    else:
                        designform.filename.data = to_edit
                    flash(f'{langs.MESSAGES[langs.PREFIX]["edit"]} {to_edit}', category='info')
                    try:
                        file_handle = open(file_to_edit, 'r')
                        page_to_edit = file_handle.read()
                        file_handle.close()
                    except IOError:
                        flash(f'{langs.MESSAGES[langs.PREFIX]["file_err"]} {to_edit}', category='danger')
                        return redirect(url_for('design_page'))
                else:
                    flash(f'{langs.MESSAGES[langs.PREFIX]["no_perm"]} {to_edit}', category='danger')
                    return redirect(url_for('design_page'))

    if request.method == 'POST':
        content = request.form
        editor_content = content.get('editor_content')
        name = content.get('name')
        time = content.get('time')
        file_to_save = content.get('filename')
        if file_to_save[-5:] == '.html' or file_to_save[-4:] == '.htm':
            print('extension .htm/.html found')
        else:
            print('extension not found, adding...')
            file_to_save = file_to_save + '.html'
            print(f'new file name: {file_to_save}')

        page_to_add = Page(name=name, file=file_to_save, time=time, owner=current_user.id, enabled=False)
        comment_to_add = Comment(owner=current_user.id, comment=langs.COMMENTS[langs.PREFIX]['newpage'],
                                 action='Page added', pagefile_related=file_to_save)

        page_exists = Page.query.filter_by(file=file_to_save).first()
        if page_exists:
            # !?
            if page_exists.name == name and page_exists.time == time:
                page_to_add = None
                comment_to_add = Comment(owner=current_user.id, comment=langs.COMMENTS[langs.PREFIX]['edit'],
                                         action='Page modified', pagefile_related=file_to_save)
            else:
                page_exists.name = name
                page_exists.time = time
                page_to_add = None
                comment_to_add = Comment(owner=current_user.id, comment=langs.COMMENTS[langs.PREFIX]['edit'],
                                         action='Page modified', pagefile_related=file_to_save)

        if len(editor_content.strip()) < 1:
            flash(langs.MESSAGES[langs.PREFIX]['emptyedit'], category='danger')
            return redirect(url_for('design_page'))
        try:
            file_save_path = os.path.join('FlaskTV', 'templates', 'info_pages', file_to_save)
            with open(file_save_path, 'w', encoding='utf-8') as file_handle:
                file_handle.write(editor_content)
            file_handle.close()
        except IOError:
            flash(langs.MESSAGES[langs.PREFIX]['io_err'], category='danger')
            return redirect(url_for('design_page'))

        db.session.add(comment_to_add)
        if page_to_add:
            db.session.add(page_to_add)
        db.session.commit()

        flash(f'{file_to_save} {langs.MESSAGES[langs.PREFIX]["savesuccess"]}', category='success')

        return redirect(url_for('design_page'))

    return render_template(f'{langs.PREFIX}/design.html', designform=designform, page_to_edit=page_to_edit,
                           editpage_query=editpage_query)


@app.route('/arrange', methods=['GET', 'POST'])
@login_required
def arrange_page():
    do_pages_exist()
    get_lang_prefix()
    arrangeform = langs.FORMS[langs.PREFIX]['arrangeform']()
    pages = Page.query.all()
    enabled = Page.query.filter_by(enabled=1).all()
    disabled = Page.query.filter_by(enabled=0).all()
    right_pane = []

    # If file is in db remove it from the right pane

    path = 'FlaskTV/templates/info_pages'
    files = os.listdir(path)
    for page in pages:
        if page.file in files:
            files.remove(page.file)

    # Left side Enabled, Right side Disabled (with files from info_pages/)

    # Temp fix
    for i in range(0, len(disabled)):
        right_pane.append(disabled[i].file)

    right_pane.extend(files)

    if request.method == 'POST':
        arrangement = request.form.get('arranged_items').split(',')
        comment = request.form.get('comments')

        if arrangement == ['']:

            flash(langs.MESSAGES[langs.PREFIX]['nomod'], category='danger')
            return redirect(url_for('arrange_page'))

        # Disabling and fix disabled list

        for page in enabled:
            if page.file not in arrangement:
                page.enabled = False

        disabled = Page.query.filter_by(enabled=0).all()

        # Drop old table to fix ordering by primary key

        try:
            db.session.query(Page).delete()
            db.session.commit()
        except exc.SQLAlchemyError:
            db.session.rollback()
            flash(langs.MESSAGES[langs.PREFIX]['rollback'], category='danger')
            return redirect(url_for('arrange_page'))

        # Write new table from pages list in the order of arrangement

        for i in range(0, len(arrangement)):
            if arrangement[i] in [p.file for p in pages]:
                for p in pages:
                    if arrangement[i] == p.file:
                        page_to_create = Page(name=p.name, file=p.file, time=p.time,
                                              owner=p.owner, enabled=True)
                        db.session.add(page_to_create)
            else:
                new_page = Page(name=arrangement[i], file=arrangement[i], time=10, owner=current_user.id, enabled=True)
                db.session.add(new_page)

        # Add back disabled pages to table

        for p in disabled:
            if p.file not in arrangement:
                disabled_to_add = Page(name=p.name, file=p.file, time=p.time,
                                       owner=p.owner, enabled=False)
                db.session.add(disabled_to_add)

        comment_to_add = Comment(owner=current_user.id, comment=comment, action='Arrangement change',
                                 pagefile_related='')
        db.session.add(comment_to_add)
        db.session.commit()
        flash(f'{len(arrangement)} {langs.MESSAGES[langs.PREFIX]["arranged"]}', category='success')
        return redirect(url_for('arrange_page'))

    return render_template(f'{langs.PREFIX}/arrange.html', pages=enabled, files=right_pane, arrangeform=arrangeform)


@app.route('/timing', methods=['GET', 'POST'])
@login_required
def timing_page():
    do_pages_exist()
    get_lang_prefix()
    timingform = langs.FORMS[langs.PREFIX]['timingform']()
    pages = Page.query.all()
    enabled = Page.query.filter_by(enabled=1).all()

    if request.method == 'POST':
        content = request.form
        comment_text = content.get('comments')
        if comment_text is None:
            comment_text = 'No comment'

        for k, v in content.items():
            if k[0:5] == 'file-':

                for page in pages:
                    if page.file == k[5:]:
                        page.time = v

        comment_to_add = Comment(owner=current_user.id, comment=comment_text, action='Timing change',
                                 pagefile_related='')
        db.session.add(comment_to_add)
        db.session.commit()
        flash(langs.MESSAGES[langs.PREFIX]['timesuccess'], category='success')
        return redirect(url_for('timing_page'))

    return render_template(f'{langs.PREFIX}/timing.html', pages=enabled, timingform=timingform)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    get_lang_prefix()
    form = langs.FORMS[langs.PREFIX]['registerform']()

    if form.validate_on_submit():

        user_to_create = User(username=form.username.data,    # type: ignore
                              email_address=form.email_address.data,    # type: ignore
                              password=form.password1.data)     # type: ignore
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'{langs.MESSAGES[langs.PREFIX]["loginsuccess"]} {form.username.data}', category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'{langs.MESSAGES[langs.PREFIX]["gen_err"]} {err_msg}', category='danger')

    return render_template(f'{langs.PREFIX}/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    get_lang_prefix()
    form = langs.FORMS[langs.PREFIX]['loginform']()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'{langs.MESSAGES[langs.PREFIX]["loginsuccess"]} {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash(langs.MESSAGES[langs.PREFIX]['login_err'], category='danger')

    return render_template(f'{langs.PREFIX}/login.html', form=form)


def db_add_comment(comment):
    try:
        db.session.add(comment)
        db.session.commit()
    except IOError or exc.SQLAlchemyError as err_msg:
        flash(f'{langs.MESSAGES[langs.PREFIX]["gen_err"]} {err_msg}', category='danger')
        return False
    return True


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    get_lang_prefix()
    removeform = langs.FORMS[langs.PREFIX]['removeform']()
    pages = Page.query.all()
    if current_user.username == 'admin':
        comments = Comment.query.all()
    else:
        comments = Comment.query.filter_by(owner=current_user.id).all()
    user = User.query.filter_by(username=current_user.username).first()
    all_users = User.query.all()

    if request.method == 'POST':
        content = request.form
        admin_clear = content.get('admin_clear')
        if admin_clear:
            try:
                num_rows_deleted = db.session.query(Comment).delete()
                db.session.commit()
                flash(f'{num_rows_deleted} {langs.MESSAGES[langs.PREFIX]["commentclear"]}', category='info')
                return redirect(url_for('profile_page'))
            except exc.SQLAlchemyError as err:
                db.session.rollback()
                flash(f'{langs.MESSAGES[langs.PREFIX]["rollback"]} ({err})', category='danger')
                return redirect(url_for('profile_page'))

        file_to_delete = content.get('toremove')[7:]
        file_to_disable = content.get('todisable')[8:]
        file_to_enable = content.get('toenable')[7:]
        file_to_rename = content.get('torename')[7:]
        file_to_edit = content.get('toedit')[5:]
        comment_text = content.get('comments')

        if len(file_to_edit) > 0:
            comment_to_add = Comment(owner=current_user.id,
                                     comment=f'{comment_text}',
                                     action='Edit', pagefile_related=file_to_edit)
            db_add_comment(comment_to_add)
            return redirect(url_for('design_page') + '?edit=' + file_to_edit)

        if len(file_to_rename) > 0:
            page = Page.query.filter_by(file=file_to_rename).first()
            page.name = comment_text
            comment_to_add = Comment(owner=current_user.id,
                                     comment=f'{langs.COMMENTS[langs.PREFIX]["rename"]} {comment_text}',
                                     action='Rename', pagefile_related=file_to_rename)
            db_add_comment(comment_to_add)

        elif len(file_to_delete) > 0:
            path = 'FlaskTV/templates/info_pages/'
            old_path = 'FlaskTV/templates/old_info_pages/'
            try:
                os.replace(path+file_to_delete, old_path+file_to_delete)
                flash(langs.MESSAGES[langs.PREFIX]['fileremoved'], category='success')
                comment_to_add = Comment(owner=current_user.id, comment=comment_text, action='Delete',
                                         pagefile_related=file_to_delete)
                db.session.add(comment_to_add)
                db.session.commit()
            except IOError or exc.SQLAlchemyError as err:
                flash(f'{langs.MESSAGES[langs.PREFIX]["gen_err"]} {err}', category='danger')
            do_pages_exist()

        elif len(file_to_disable) > 0:
            page = Page.query.filter_by(file=file_to_disable).first()
            page.enabled = False
            comment_to_add = Comment(owner=current_user.id, comment=comment_text, action='Disable',
                                     pagefile_related=file_to_disable)
            db_add_comment(comment_to_add)

        elif len(file_to_enable) > 0:
            page = Page.query.filter_by(file=file_to_enable).first()
            page.enabled = True
            comment_to_add = Comment(owner=current_user.id, comment=comment_text, action='Enable',
                                     pagefile_related=file_to_enable)
            db_add_comment(comment_to_add)

        return redirect(url_for('profile_page'))

    return render_template(f'{langs.PREFIX}/profile.html', users=all_users, user=user, removeform=removeform,
                           comments=comments, pages=pages, actions=langs.ACTIONS[langs.PREFIX])


@app.route('/logout')
def logout_page():
    logout_user()
    flash(langs.MESSAGES[langs.PREFIX]['logout'], category='info')
    return redirect(url_for('home_page'))


@app.route('/uploads/<path:name>')
def download_file(name):
    # return send_from_directory(app.config["UPLOAD_FOLDER"], name, as_attachment=True)
    return redirect(f'/static/{name}')


def allowed_file(filename, ext):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ext


ALLOWED_PAGE_FILES = {'htm', 'html'}


@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    get_lang_prefix()
    page_dir = './FlaskTV/templates/info_pages'
    if request.method == 'POST':

        # print(*request.files)
        if 'file-0' not in request.files:
            flash(langs.MESSAGES[langs.PREFIX]['nofilereq'], category='danger')
            return redirect(url_for('upload_page'))

        file = request.files['file-0']
        if file.filename == '':
            flash(langs.MESSAGES[langs.PREFIX]['nofilesel'], category='danger')
            return redirect(url_for('upload_page'))
        if file and allowed_file(file.filename, ALLOWED_PAGE_FILES):
            filename = secure_filename(file.filename)

            if os.path.isfile(os.path.join(page_dir, filename)):
                flash(f'{filename} {langs.MESSAGES[langs.PREFIX]["file_exists"]}', category='danger')
                return redirect(url_for('upload_page'))

            file.save(os.path.join(page_dir, filename))
            flash(f'{filename} {langs.MESSAGES[langs.PREFIX]["send_success"]}', category='success')
            comment_to_add = Comment(owner=current_user.id, comment='File upload', action='Upload',
                                     pagefile_related=filename)
            db_add_comment(comment_to_add)
            return redirect(url_for('upload_page'))

    return render_template(f'{langs.PREFIX}/upload.html')


@app.route('/uadmin', methods=['GET', 'POST'])
@login_required
def uadmin_page():
    get_lang_prefix()

    if current_user.username != 'admin' or current_user.id != 5:
        flash(langs.MESSAGES[langs.PREFIX]['noadmin'], category='danger')
        return redirect(url_for('home_page'))

    uadminform = langs.FORMS[langs.PREFIX]['uadminform']()
    if request.method == 'POST':
        if uadminform.validate_on_submit():
            to_do = request.form.get('todo')
            user_to_change = request.form.get('user_list')
            new_password = request.form.get('comments')

            if to_do == 'delete':
                print(f'Deleting {user_to_change}')
                if new_password == 'YES':
                    try:
                        poor_user_instance = User.query.filter_by(username=user_to_change).first()
                        users_pages = Page.query.filter(Page.owner == poor_user_instance.id).all()
                        for page in users_pages:
                            # give all of the poor user's pages to admin
                            page.owner = 5
                        delete_user = User.query.filter(User.username == user_to_change).delete()
                        db.session.commit()
                        if delete_user:
                            print('Success.')
                        flash(langs.MESSAGES[langs.PREFIX]['userdelete'], category='success')
                        return redirect(url_for('uadmin_page'))
                    except exc.SQLAlchemyError:
                        db.session.rollback()
                        flash(langs.MESSAGES[langs.PREFIX]['rollback'], category='danger')
                        return redirect(url_for('uadmin_page'))
                else:
                    flash(langs.MESSAGES[langs.PREFIX]['noconfirm'], category='danger')
                    print('Cancelling')
                    return redirect(url_for('uadmin_page'))

            if to_do == 'change_pass':
                print(f'Changing pass of {user_to_change}')
                user_instance = User.query.filter(User.username == user_to_change).first()
                try:
                    user_instance.password = new_password
                    db.session.commit()
                    flash(langs.MESSAGES[langs.PREFIX]['passchange'], category='success')
                    return redirect(url_for('uadmin_page'))
                except exc.SQLAlchemyError:
                    db.session.rollback()
                    flash(langs.MESSAGES[langs.PREFIX]['rollback'], category='danger')
                    return redirect(url_for('uadmin_page'))

            return redirect(url_for('uadmin_page'))

    return render_template(f'{langs.PREFIX}/uadmin.html', uadminform=uadminform)


@app.route('/preview')
@login_required
def preview_page():
    page = request.args.get('page')
    if not page:
        return redirect(url_for('home_page'))

    page_file = os.path.join(os.getcwd(), 'FlaskTV', 'templates', 'info_pages', page)
    if os.path.isfile(page_file):
        return render_template(f'preview.html', page=page)
    else:
        return redirect(url_for('home_page'))


