# Generated by Django 3.1.7 on 2021-03-20 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_comment_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='commenter_username',
            field=models.CharField(default=2, max_length=100),
            preserve_default=False,
        ),
    ]
