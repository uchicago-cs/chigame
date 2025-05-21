from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='twine_file',
            field=models.FileField(blank=True, null=True, upload_to='twine_games/'),
        ),
        migrations.AddField(
            model_name='game',
            name='twine_file_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='twine_file_content',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
