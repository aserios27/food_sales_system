from django import forms
from sales.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product  # 사용할 모델
        fields = ['pcode', 'pname', 'pclass', 'pMain', 'pSoup', 'pSub1', 'pSub2', 'pSub3', 'unitprice', \
                  'discountrate', 'modify_date', 'imgfile']
        #
        # widgets = {
        #     'pcode': forms.TextInput(attrs={'class': 'form-control'}),
        #     'pname': forms.TextInput(attrs={'class': 'form-control'}),
        #     'unitprice': forms.TextInput(attrs={'class': 'form-control'}),
        #     'discountrate': forms.TextInput(attrs={'class': 'form-control'}),
        # }

        labels = {
            'pcode': '식단 코드 ',
            'pname': '식단 명 ',
            'unitprice': '단  가 ',
            'discountrate': '할 인 율 ',
            'imgfile' : '식단 사진',
        }
