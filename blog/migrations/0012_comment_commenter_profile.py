# Generated by Django 3.1.7 on 2021-03-20 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile_about'),
        ('blog', '0011_comment_commenter_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='commenter_profile',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commenter_profile', to='users.profile'),
        ),
    ]
