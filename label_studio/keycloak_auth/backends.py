from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import authentication

import requests

from projects.models import Project, ProjectMember

from organizations.models import Organization

from keycloak_auth.keycloak_utils import check_user_in_keycloak

# url = "http://localhost:8081/realms/test/protocol/openid-connect/token"

# payload = 'username=test_admin&password=TESTpSSWrd&grant_type=password'

# headers = {
#   'Content-Type': 'application/x-www-form-urlencoded'
# }

# response = requests.request("POST", url, headers=headers, data=payload)


class ExampleAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request, email, password):
        user_in_keycloak = check_user_in_keycloak(email, password)
        if not user_in_keycloak:
            return None # authentication did not succeed
        UserModel = get_user_model()
        email_field_name = UserModel.get_email_field_name()
        user, _ = UserModel.objects.update_or_create(
            username=email,
            defaults={
                f'{email_field_name}': email, 
            }
        )

        user.password = make_password(password)
        user.save()

        organization = Organization.objects.first()
        if not user.organizations.filter(pk=organization.pk).exists():
            organization.users.add(user)

        # for project in Project.objects.all():
        #     ProjectMember.objects.get_or_create(
        #         project=project,
        #         user=user,
        #         defaults={
        #             'user_role': 'ANNOTATOR'
        #         }
        #     )

        return user # authentication successful