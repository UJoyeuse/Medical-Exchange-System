from django import forms


class CreateTransactionForm(forms.Form):
    grade1_litters = forms.IntegerField()
    grade2_litters = forms.IntegerField()


class SearchrRequests(forms.Form):
    date = forms.DateField(required=False)
    is_range_date = forms.CharField(required=False)

class makingRange(forms.Form):
    start_date=forms.DateTimeField(required=False)
    end_date=forms.DateTimeField(required=False)


