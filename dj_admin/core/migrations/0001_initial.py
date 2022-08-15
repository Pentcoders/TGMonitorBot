from django.db import migrations
from envparse import env

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    def generate_superuser(apps, schema_editor):
        from django.contrib.auth.models import User

        DJANGO_SU_NAME = env.str('DJANGO_SU_NAME')
        DJANGO_SU_EMAIL = env.str('DJANGO_SU_EMAIL')
        DJANGO_SU_PASSWORD = env.str('DJANGO_SU_PASSWORD')

        superuser = User.objects.create_superuser(
            username=DJANGO_SU_NAME,
            email=DJANGO_SU_EMAIL,
            password=DJANGO_SU_PASSWORD)

        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]

