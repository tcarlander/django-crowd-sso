from django import forms


class UsersForm(forms.Form):
    email_list = forms.CharField(label='Your List',widget=forms.Textarea, max_length=1000)