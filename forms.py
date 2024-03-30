from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms.validators import InputRequired

class RegisterForm(FlaskForm):
    UserName = StringField('UserName:',validators=[DataRequired(), Length(min=2,max=10)])
    #Email = StringField('Email:',validators=[DataRequired(), Email()])
    Password = PasswordField('Password:',validators=[DataRequired()])
    ConfirmPassword = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    Age = IntegerField('Age', validators=[InputRequired()])  # Add an Age field
    PhoneNumber = StringField('Phone Number', validators=[InputRequired(), Length(min=10, max=15)])

    Submit = SubmitField('Register Here!')

class LoginForm(FlaskForm):
    UserName = StringField('UserName:',validators=[DataRequired()])
    Password = PasswordField('Password:',validators=[DataRequired()])
    Submit = SubmitField('Login Here!')
