# Generated by Django 4.1.7 on 2023-12-18 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0003_player_avatar_id'),
        ('TTTGame', '0002_manual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tttboard',
            name='turn',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='tttboard',
            name='turn_of_team',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='tttplayer',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainpage.player'),
        ),
    ]
