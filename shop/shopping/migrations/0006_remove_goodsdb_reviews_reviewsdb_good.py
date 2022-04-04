# Generated by Django 4.0.3 on 2022-04-03 12:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0005_reviewsdb_goodsdb'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goodsdb',
            name='reviews',
        ),
        migrations.AddField(
            model_name='reviewsdb',
            name='good',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='review_for_good', to='shopping.goodsdb'),
        ),
    ]
