# Generated by Django 5.2.1 on 2025-05-23 21:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dimensionnement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consommation_journaliere_wh', models.IntegerField()),
                ('profil_charge', models.JSONField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('marge_securite_pct', models.IntegerField(default=20)),
                ('rendement_systeme_pct', models.IntegerField(default=85)),
                ('nombre_panneaux', models.IntegerField(null=True)),
                ('puissance_panneau_w', models.IntegerField(null=True)),
                ('capacite_batterie_ah', models.IntegerField(null=True)),
                ('tension_systeme_v', models.IntegerField(null=True)),
                ('regulateur_data', models.JSONField(null=True)),
                ('onduleur_data', models.JSONField(null=True)),
                ('irradiation_moyenne_kwh_m2_j', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Dimensionnement',
                'verbose_name_plural': 'Dimensionnements',
                'ordering': ['-created_at'],
            },
        ),
    ]
