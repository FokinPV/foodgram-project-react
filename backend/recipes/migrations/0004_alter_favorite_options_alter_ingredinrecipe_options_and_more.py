# Generated by Django 4.1.7 on 2023-03-18 10:42

import colorfield.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_shoppinglist_recipe_alter_shoppinglist_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'Избранный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='ingredinrecipe',
            options={'verbose_name': 'Количество ингредиентов', 'verbose_name_plural': 'Количество ингредиентов'},
        ),
        migrations.AlterModelOptions(
            name='shoppinglist',
            options={'verbose_name': 'Рецепт в корзине', 'verbose_name_plural': 'Рецепт в корзине'},
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique favorite',
        ),
        migrations.RemoveConstraint(
            model_name='ingredinrecipe',
            name='unique ingredient in recipe',
        ),
        migrations.RemoveConstraint(
            model_name='shoppinglist',
            name='unique recipe in shoplist',
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления (в минутах)'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=18, samples=None, verbose_name='Цвет в HEX'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='уникальный избранный'),
        ),
        migrations.AddConstraint(
            model_name='ingredinrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='уникальный ингредиент в рецепте'),
        ),
        migrations.AddConstraint(
            model_name='shoppinglist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='уникальный рецепт в корзине'),
        ),
    ]