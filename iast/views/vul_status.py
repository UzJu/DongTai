#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: owefsad@huoxian.cn
# project: dongtai-webapi

# status
from dongtai.models.vulnerablity import IastVulnerabilityModel
from dongtai.models.vulnerablity import IastVulnerabilityStatus

from dongtai.endpoint import R
from dongtai.endpoint import UserEndPoint
from django.utils.translation import gettext_lazy as _
from iast.utils import extend_schema_with_envcheck
import logging

logger = logging.getLogger('dongtai-webapi')

class VulStatus(UserEndPoint):
    name = "api-v1-vuln-status"
    description = _("Modify the vulnerability status")

    @extend_schema_with_envcheck(
        [],
        {
            'id': 1,
            'status': 'status',
            'status_id': 1
        },
        tags=[_('Vulnerability')],
        summary=_("Vulnerability Status Modify"),
        description=_("""Modify the vulnerability status of the specified id. 
        The status is specified by the following two parameters. 
        Status corresponds to the status noun and status_id corresponds to the status id. 
        Both can be obtained from the vulnerability status list API, and status_id is preferred."""
                      ),
    )
    def post(self, request):
        vul_id = request.data.get('id')
        status = request.data.get('status', None)
        status_id = request.data.get('status_id', None)
        if vul_id and (status or status_id):
            vul_model = IastVulnerabilityModel.objects.filter(
                id=vul_id,
                agent__in=self.get_auth_agents_with_user(
                    request.user)).first()
            if status_id:
                try:
                    status_ = IastVulnerabilityStatus.objects.get(status_id)
                except Exception as e:
                    logger.error(e)
                    print(e)
            else:
                status_, iscreate = IastVulnerabilityStatus.objects.get_or_create(
                    name=status)
            try:
                vul_model.status_id = status_.id
                vul_model.save()
                msg = _('Vulnerability status is modified to {}').format(
                    status)
                return R.success(msg=msg)
            except:
                pass
        msg = _('Incorrect parameter')
        return R.failure(msg=msg)
