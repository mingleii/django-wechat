#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/12/2 0002"
"""
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType


class CustomAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        if request.POST.get('action'):
            action = self.get_actions(request)[request.POST['action']][0]
            if hasattr(action, "no_select_action"):
                post = request.POST.copy()
                post.setlist(admin.helpers.ACTION_CHECKBOX_NAME, [None])
                request.POST = post
            elif hasattr(action, "all_select_action"):
                post = request.POST.copy()
                post.setlist(admin.helpers.ACTION_CHECKBOX_NAME,
                             self.model.objects.values_list('id', flat=True))
                request.POST = post

        return admin.ModelAdmin.changelist_view(self, request, extra_context)