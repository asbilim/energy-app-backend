# Generated by Django 5.2.1 on 2025-05-23 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Composant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('panneau', 'Panneau'), ('batterie', 'Batterie'), ('regulateur', 'Régulateur'), ('onduleur', 'Onduleur')], max_length=20)),
                ('marque', models.CharField(max_length=100)),
                ('modele', models.CharField(max_length=100)),
                ('specifications', models.JSONField()),
                ('prix_eur', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Composant',
                'verbose_name_plural': 'Composants',
                'ordering': ['type', 'marque', 'modele'],
                'unique_together': {('type', 'marque', 'modele')},
            },
        ),
    ]
