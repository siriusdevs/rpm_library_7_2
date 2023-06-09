# Generated by Django 4.1.7 on 2023-04-12 14:09

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('library_app', '0002_alter_book_type_alter_genre_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookClient',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='created')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library_app.book')),
            ],
            options={
                'db_table': '"library"."book_client"',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='created')),
                ('modified', models.DateTimeField(blank=True, default=datetime.datetime.now, verbose_name='modified')),
                ('money', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('books', models.ManyToManyField(through='library_app.BookClient', to='library_app.book')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
                'db_table': '"library"."client"',
            },
        ),
        migrations.AddField(
            model_name='bookclient',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library_app.client'),
        ),
        migrations.AlterUniqueTogether(
            name='bookclient',
            unique_together={('book', 'client')},
        ),
    ]
