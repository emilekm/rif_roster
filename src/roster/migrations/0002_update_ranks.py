from django.db import migrations, models


def update_ranks(apps, schema_editor):
    SquadRole = apps.get_model('roster', 'SquadRole')
    for r in SquadRole.objects.all():
        if r.role is not 0:
            r.role += 2
            r.save()


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_ranks),
        migrations.AddField(
            model_name='squad',
            name='short',
            field=models.CharField(default='', max_length=3),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='player',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='squadrole',
            name='role',
            field=models.IntegerField(choices=[(0, 'SCO'), (1, 'CO'), (2, 'XO'), (3, 'HCO'), (4, 'SL'), (5, 'NCO'), (6, 'Grunt'), (7, 'Reserve')], default=7),
        ),
    ]
