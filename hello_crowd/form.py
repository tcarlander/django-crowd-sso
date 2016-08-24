from django import forms


class UsersForm(forms.Form):
    user_list = forms.CharField(label='Your List',widget=forms.Textarea, max_length=1000)