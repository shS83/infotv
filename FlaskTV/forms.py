from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, Optional, ValidationError
from FlaskTV.models import User


class RegisterForm(FlaskForm):

    @staticmethod
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username.')

    @staticmethod
    def validate_email_address(self, email_to_check):
        email = User.query.filter_by(email_address=email_to_check.data).first()
        if email:
            raise ValidationError('E-mail address already exists! Please try a different e-mail address.')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='E-mail Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')


class RegisterForm_fi(FlaskForm):

    @staticmethod
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Käyttäjä on jo olemassa. Käytä toista käyttäjänimeä.')

    @staticmethod
    def validate_email_address(self, email_to_check):
        email = User.query.filter_by(email_address=email_to_check.data).first()
        if email:
            raise ValidationError('Sähköpostiosoite on jo rekisteröity. Käytä toista sähköpostiosoitetta.')

    username = StringField(label='Käyttäjänimi:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Sähköpostiosoite:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Salasana:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Varmista salasana:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Luo tunnus')


class LoginForm(FlaskForm):

    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Log in')


class LoginForm_fi(FlaskForm):

    username = StringField(label='Käyttäjänimi:', validators=[DataRequired()])
    password = PasswordField(label='Salasana:', validators=[DataRequired()])
    submit = SubmitField(label='Kirjaudu sisään')


class HTMLImportForm(FlaskForm):
    html_file = FileField(validators=[FileRequired(), FileAllowed(['html'])])


class PowerPointImportForm(FlaskForm):
    powerpoint_file = FileField(validators=[FileRequired(), FileAllowed(['ppt', 'pptx'])])


class WordImportForm(FlaskForm):
    word_file = FileField(validators=[FileRequired(), FileAllowed(['doc', 'docx'])])


class PDFImportForm(FlaskForm):
    pdf_file = FileField(validators=[FileRequired(), FileAllowed(['pdf'])])


class DesignForm(FlaskForm):
    name = StringField(label='Page description:', validators=[DataRequired()])
    filename = StringField(label='File name to save:', validators=[DataRequired()])
    time = IntegerField(label='Time on display:', validators=[DataRequired()])
    submit = SubmitField(label='Save')


class DesignForm_fi(FlaskForm):
    name = StringField(label='Sivun kuvaus:', validators=[DataRequired()])
    filename = StringField(label='Tiedoston nimi:', validators=[DataRequired()])
    time = IntegerField(label='Näyttöaika:', validators=[DataRequired()])
    submit = SubmitField(label='Tallenna')


class ArrangeForm(FlaskForm):
    comments = StringField(label='Comment to add:', validators=[Optional()])
    submit = SubmitField(label='Save order')


class ArrangeForm_fi(FlaskForm):
    comments = StringField(label='Lisää kommentti:', validators=[Optional()])
    submit = SubmitField(label='Tallenna järjestys')


class RemoveForm(FlaskForm):
    comments = StringField(label='Comment to add:', validators=[Optional()])
    submit = SubmitField(label='Modify')


class RemoveForm_fi(FlaskForm):
    comments = StringField(label='Lisää kommentti:', validators=[Optional()])
    submit = SubmitField(label='Muokkaa')


class TimingForm(FlaskForm):
    comments = StringField(label='Comment to add:', validators=[Optional()])
    submit = SubmitField(label='Save timing')


class TimingForm_fi(FlaskForm):
    comments = StringField(label='Lisää kommentti:', validators=[Optional()])
    submit = SubmitField(label='Tallenna ajastus')


class UAdminForm(FlaskForm):
    user_list = SelectField(label='Select a user')
    comments = StringField(label='Add a comment:', validators=[DataRequired()])
    submit = SubmitField(label='Confirm')

    def __init__(self, *args, **kwargs):
        super(UAdminForm, self).__init__(*args, **kwargs)
        self.user_list.choices = [(u.username, u.username) for u in User.query.filter(User.id != 5).all()]


class UAdminForm_fi(FlaskForm):
    user_list = SelectField(label='Valitse käyttäjä')
    comments = StringField(label='Lisää kommentti:', validators=[DataRequired()])
    submit = SubmitField(label='Vahvista')

    def __init__(self, *args, **kwargs):
        super(UAdminForm_fi, self).__init__(*args, **kwargs)
        self.user_list.choices = [(u.username, u.username) for u in User.query.filter(User.id != 5).all()]


