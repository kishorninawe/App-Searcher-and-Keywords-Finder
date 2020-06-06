from django import forms

	
class URLForm(forms.Form):
	url = forms.URLField(label='URL',
						 widget=forms.URLInput(
							 attrs={
								 'class': 'form-control',
								 'placeholder': 'Enter a URL',
								 'name': 'url',
								 'id': 'url'
							 }))
