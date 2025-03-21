# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('아이디', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    submit = SubmitField('로그인')

class SignupForm(FlaskForm):
    username = StringField('아이디', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('비밀번호', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('비밀번호 확인', validators=[DataRequired(), EqualTo('password')])
    agree = BooleanField('이용 약관에 동의합니다.', validators=[DataRequired()])
    submit = SubmitField('가입')

class ChatForm(FlaskForm):
  message = TextAreaField('메시지',validators=[DataRequired()])
  submit = SubmitField('Send')