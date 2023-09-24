from django.contrib import admin

from .models import (Ingredient, Tag, Recipe,
                     IngredientAmount, ShoppingCart, FavoriteRecipe)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_point',]
    list_filter = ('name',)
    ordering = ('id',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    ordering = ('id',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('created', 'name', 'author', 'favorite_count')
    list_editable = ('name',)
    list_filter = ('name', 'author', 'tags')
    ordering = ('created',)
    readonly_fields = ('favorite_count',)

    def favorite_count(self, obj):
        return obj.favorite_recipe.count()

    favorite_count.short_description = 'Izbrannoe'


class AmountAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'ingredient', 'recipe')
    ordering = ('id',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    ordering = ('user',)


class FacRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    ordering = ('user',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientAmount, AmountAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(FavoriteRecipe, FacRecipeAdmin)
