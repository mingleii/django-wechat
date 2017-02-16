#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/11/25 0025"
"""
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from wechat.models import WechatMenuSubConfig, WechatMenuConfig


class WechatMenuConfigAdminForm(forms.ModelForm):
    level_2 = forms.ModelMultipleChoiceField(
        queryset=WechatMenuSubConfig.objects.filter(is_display=True),
        required=False,
        help_text=u"二级菜单最多7个",
        label=u"二级菜单",
        widget=FilteredSelectMultiple(verbose_name=u'任务图文',
                                      is_stacked=False))

    class Meta:
        model = WechatMenuConfig
        exclude = ("ctime", "utime")

    def __init__(self, *args, **kwargs):
        super(WechatMenuConfigAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['level_2'].initial = self.instance.level_2.all()

    def save(self, commit=True):
        result = super(WechatMenuConfigAdminForm, self).save(commit=False)
        if commit:
            result.save()
        if result.pk:
            result.level_2 = self.cleaned_data['level_2']
            self.save_m2m()
        return result