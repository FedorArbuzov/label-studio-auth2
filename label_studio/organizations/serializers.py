"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
from collections import OrderedDict

import ujson as json
from django.db.models import Q
from drf_dynamic_fields import DynamicFieldsMixin
from organizations.models import Organization, OrganizationMember
from projects.models import Project, Annotation
from tasks.models import ReviewerAnnotationLog
from rest_framework import serializers
from users.serializers import UserSerializer


class OrganizationIdSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'title', 'contact_info']


class OrganizationSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class OrganizationMemberSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = OrganizationMember
        fields = ['id', 'organization', 'user']


class UserSerializerWithProjects(UserSerializer):
    created_projects = serializers.SerializerMethodField(read_only=True)
    contributed_to_projects = serializers.SerializerMethodField(read_only=True)
    have_access_to_projects = serializers.SerializerMethodField(read_only=True)
    annotation_count = serializers.SerializerMethodField(read_only=True)
    annotation_updated_count = serializers.SerializerMethodField(read_only=True)

    def get_annotation_count(self, user):
        return Annotation.objects.filter(completed_by=user).count()

    def get_annotation_updated_count(self, user):
        annotations = Annotation.objects.filter(completed_by=user)
        reviewer_logs = ReviewerAnnotationLog.objects.filter(annotation__in=annotations)
        return reviewer_logs.count()

    def get_have_access_to_projects(self, user):
        all_projects = Project.objects.all().values('id', 'title')
        accessible_projects = Project.objects.filter(members__user=user).values_list('id', flat=True)

        projects_with_access = []
        for project in all_projects:
            project['has_access'] = project['id'] in accessible_projects
            projects_with_access.append(project)

        return projects_with_access

    def get_created_projects(self, user):
        if not self.context.get('contributed_to_projects', False):
            return None

        current_user = self.context['request'].user
        return user.created_projects.filter(organization=current_user.active_organization).values('id', 'title')

    def get_contributed_to_projects(self, user):
        if not self.context.get('contributed_to_projects', False):
            return None

        current_user = self.context['request'].user
        projects = user.annotations.filter(project__organization=current_user.active_organization).values(
            'project__id', 'project__title'
        )
        contributed_to = [(json.dumps({'id': p['project__id'], 'title': p['project__title']}), 0) for p in projects]
        contributed_to = OrderedDict(contributed_to)  # remove duplicates without ordering losing
        return [json.loads(key) for key in contributed_to]

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('created_projects',
         'contributed_to_projects', 'have_access_to_projects', 'role', 'annotation_count', 'annotation_updated_count')


class OrganizationMemberUserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """Adds all user properties"""

    user = UserSerializerWithProjects()

    class Meta:
        model = OrganizationMember
        fields = ['id', 'organization', 'user']


class OrganizationInviteSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)
    invite_url = serializers.CharField(required=False)


class OrganizationsParamsSerializer(serializers.Serializer):
    active = serializers.BooleanField(required=False, default=False)
    contributed_to_projects = serializers.BooleanField(required=False, default=False)
