# Generated migration: добавление поля tint_service в Booking
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='tint_service',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bookings',
                to='services.tintservice',
                verbose_name='Услуга тонировки'
            ),
        ),
        migrations.AlterField(
            model_name='booking',
            name='armor_package',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bookings',
                to='services.armorpackage',
                verbose_name='Пакет бронирования'
            ),
        ),
        migrations.AlterField(
            model_name='booking',
            name='tint_film_percent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bookings',
                to='services.filmtintpercent',
                verbose_name='Плёнка и процент'
            ),
        ),
    ]

