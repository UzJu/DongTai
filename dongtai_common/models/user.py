#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:owefsad
# datetime:2021/1/25 下午6:43
# software: PyCharm
# project: dongtai-models

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _

from dongtai_common.models.department import Department
from dongtai_common.utils.settings import get_managed


class PermissionsMixin(models.Model):
    department = models.ManyToManyField(
        Department,
        verbose_name=_('department'),
        blank=True,
        help_text=_(
            'The department this user belongs to. A user will get all permissions '
            'granted to each of their department.'
        ),
        related_name="users",
        related_query_name="user",
    )

    class Meta:
        abstract = True


class SaaSUserManager(UserManager):

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', 0)
        return self._create_user(username, email, password, **extra_fields)

    def create_talent_user(self,
                           username,
                           email=None,
                           password=None,
                           **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', 2)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') != 2:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def create_system_user(self,
                           username,
                           email=None,
                           password=None,
                           **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', 1)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') != 1:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    is_superuser = models.IntegerField(default=0)
    phone = models.CharField(max_length=15)
    default_language = models.CharField(max_length=15)
    objects = SaaSUserManager()
    using_department = None

    class Meta(AbstractUser.Meta):
        db_table = 'auth_user'

    def is_system_admin(self):
        return self.is_superuser == 1

    def is_talent_admin(self):
        return self.is_superuser == 2 or self.is_superuser == 1 or self.is_superuser == 6

    def get_talent(self):
        try:
            department = self.department.get() if self.department else None
            talent = department.talent.get() if department else None
        except Exception as e:
            talent = None
        return talent

    def get_department(self):
        try:
            department = self.department.get()
        except Exception as e:
            department = None
        return department

    @property
    def is_department_admin(self):
        return Department.objects.filter(principal_id=self.id).exists()

    def get_relative_department(self) -> QuerySet:
        from functools import reduce
        from operator import ior
        department = self.get_department()
        principal_departments = Department.objects.filter(
            Q(principal_id=self.id) | Q(pk=department.id))
        qs = Department.objects.none()
        qss = [
            Q(department_path__startswith=pdepartment.department_path)
            for pdepartment in principal_departments
        ]
        totals = reduce(ior, qss, qs)
        if not totals:
            total_dep = Department.objects.none()
        else:
            total_dep = Department.objects.filter(totals)
        return Department.objects.filter(pk__in=[i.id for i in total_dep])

    def get_using_department(self):
        if self.using_department:
            return self.using_department
        return self.get_department()
