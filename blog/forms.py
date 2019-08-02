from django import forms
from blog import models
from django.core.exceptions import ValidationError

class Register_Form(forms.Form):
    username = forms.CharField(
        max_length=16,
        label='用户名',
        error_messages={
            "max_length": "用户名最长为16",
            "required": "用户名不能为空"
        },
        widget=forms.widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )

    password = forms.CharField(
        min_length=6,
        label='密码',
        error_messages={
            "min_length": "密码最短为6",
            "required": "密码不能为空"
        },
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'form-control'},
            render_value=True
        )
    )

    re_password = forms.CharField(
        min_length=6,
        label='密码',
        error_messages={
            "min_length": "确认密码最短为6",
            "required": "确认密码不能为空"
        },
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'form-control'},
            render_value=True
        )
    )

    email = forms.CharField(
        label='邮箱',
        error_messages={
            'invalid': '邮箱格式不正确',
            'required': '邮箱不能为空'
        },
        widget=forms.widgets.EmailInput(
            attrs={'class': 'form-control'}
        )
    )

    #自定义校验规则,在相应的字段前加clean_
    def clean_username(self):
        username=self.cleaned_data.get('username')
        is_exist=models.UserInfo.objects.filter(username=username)
        if is_exist:
            self.add_error("username",ValidationError("用户名已存在"))
        else:
            return username

    def clean_password(self):
        pwd=self.cleaned_data.get('password')
        if pwd in ['123456','666666','111111']:
            self.add_error('password',ValidationError('密码过于简单'))
        else:
            return pwd


    #clean,全局钩子函数
    def clean(self):
        password=self.cleaned_data.get('password')
        re_password=self.cleaned_data.get('re_password')
        if re_password and re_password!=password:
            self.add_error('re_password',ValidationError("两次密码不一样"))
        else:
            return self.cleaned_data