from django.core.management.base import BaseCommand
from projects.models import Project, ProjectMember
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        ProjectMember.objects.all().delete()
        # users = User.objects.all()
        # for user in users:
        #     print(user)
        #     #  projects = Project.objects.filter(members__user=user)
        #     #  for project in projects:
        #     #      ProjectMember.objects.get_or_create(project=project, user=user)
        # user = users[5]
        # project = Project.objects.get(id=6)
        # ProjectMember.objects.get_or_create(project=project, user=user)