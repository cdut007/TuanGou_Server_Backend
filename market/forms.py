from datetime import datetime
from django import forms
from models import GroupBuy
from suit.widgets import SuitSplitDateTimeWidget

class GroupBuyForm(forms.ModelForm):
    class Meta:
        model = GroupBuy
        exclude = ['add_time']
        widgets = {
            'start_time': SuitSplitDateTimeWidget,
            'end_time': SuitSplitDateTimeWidget
        }

    def save(self, commit=True):
        instance = super(GroupBuyForm, self).save(commit=False)
        instance.add_time = datetime.now()
        if commit:
            instance.save()
        return instance
