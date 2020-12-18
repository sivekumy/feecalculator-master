from wtforms import Form, TextField, TextAreaField, SubmitField, validators, ValidationError

#class for feedback form
class ContactForm(Form):
  name = TextField("Name", [validators.Required("Please enter your name.")])
  email = TextField("Email", [validators.Required(), validators.Email("Please enter your email address.")])
  subject = TextField("Subject", [validators.Required("Please enter a subject.")])
  message = TextAreaField("Message", [validators.Required("Please enter a message.")])
  submit = SubmitField("Send")