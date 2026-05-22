from django import forms
from django.contrib.auth.models import Permission
from .models import Role


class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permissions",
        help_text="Assign specific permissions to this role.",
    )

    class Meta:
        model = Role
        fields = ["name", "display_name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({"class": "form-control"})
        if self.instance.pk:
            self.fields["permissions"].initial = self.instance.group.permissions.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            instance.group.permissions.set(self.cleaned_data.get("permissions", []))
        return instance
