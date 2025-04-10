from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, \
    HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, URL, Optional, NumberRange


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    bio = TextAreaField('О себе', validators=[Optional(), Length(max=500)])
    avatar = FileField('Аватар', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Только изображения')
    ])
    submit = SubmitField('Зарегистрироваться')


class PostForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(min=3, max=100)])
    content = TextAreaField('Содержание', validators=[DataRequired(), Length(min=10, max=5000)])
    media_files = MultipleFileField('Медиафайлы (до 3)', validators=[Optional()])
    place_id = HiddenField('ID места', validators=[DataRequired()])
    place_search = StringField('Поиск места', validators=[DataRequired()])
    submit = SubmitField('Создать пост')


class CommentForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Отправить')


class PlaceForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Описание', validators=[DataRequired(), Length(min=10, max=2000)])
    address = StringField('Адрес', validators=[DataRequired(), Length(min=5, max=200)])
    latitude = FloatField('Широта', validators=[DataRequired(), NumberRange(min=-90, max=90)])
    longitude = FloatField('Долгота', validators=[DataRequired(), NumberRange(min=-180, max=180)])
    place_image = FileField('Изображение места', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Только изображения')
    ])
    submit = SubmitField('Добавить место')


class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    bio = TextAreaField('О себе', validators=[Optional(), Length(max=500)])
    avatar = FileField('Аватар', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Только изображения')
    ])
    submit = SubmitField('Обновить профиль')
