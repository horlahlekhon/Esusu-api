# Generated by Django 2.2.4 on 2019-09-08 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esusu', '0004_auto_20190908_0554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contribution',
            name='contrib_amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='group',
            name='contrib_amount',
            field=models.IntegerField(default=0),
        ),
    ]
