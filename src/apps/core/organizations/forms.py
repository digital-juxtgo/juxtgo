from django import forms


class OrganizationForm(forms.Form):
    """Simple form for creating a new organisation."""

    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"placeholder": "Organization name", "class": "form-control"}
        ),
        label="Organization Name",
    )
