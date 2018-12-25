from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, MultipleFileField
from wtforms.validators import InputRequired, Email, ValidationError, EqualTo


def valid_password(form, field):
  """
  Validates password requirements
  
  Custom validator for ensuring passwords are secure
  
  Args:
    form (FlaskForm): A FlaskForm
    field (Password): A field containing text data(password)
  
  Raises:
    ValidationError: [description]
  
  Returns:
    ValidationError: If requirements not met, a validation error with message is thrown. Otherwise no return.
  """

  message = "Password must be at least 8 characters long. It must contain at least 1 alphabetic character (a-z or A-Z), and 1 number (0-9)"
  has_letter = False
  has_number = False

  if len(field.data) < 8:
    raise ValidationError('Password must be at least 8 characters long')

  for c in field.data:
    if c.isalpha():
      has_letter = True
    if c.isdigit():
      has_number = True

  if not (has_letter and has_number):  # If password doesn't meet requirements
    raise ValidationError(message)


class RegisterForm(FlaskForm):
  """
  Registration form to ensure validation
  
  Creates a flask form so users can register for a new account. Validates formatting and password requirements.
  
  """

  email = StringField('email', [
      InputRequired("Please enter your email address"),
      Email("Invalid email address")
  ])
  password = PasswordField('Password', [
      InputRequired("Please enter your password"),
      EqualTo('password_confirm', 'Passwords do not match'), valid_password
  ])
  password_confirm = PasswordField('Repeat Password')


class LoginForm(FlaskForm):
  """
  Log in form for user accounts
  
  Validates the form requirements for user account log in.

  """
  email = StringField('email', [
      InputRequired("Please enter your email address"),
      Email("Invalid email address")
  ])
  password = PasswordField('Password',
                           [InputRequired("Please enter your password")])
  remember_check = BooleanField('remember_check')


class ResetForm(FlaskForm):
  """
  Password validator when resetting user password
  """

  password = PasswordField('Password', [
      InputRequired("Please enter your password"),
      EqualTo('password_confirm', 'Passwords do not match'), valid_password
  ])
  password_confirm = PasswordField('Repeat Password')