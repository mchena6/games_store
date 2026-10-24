from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'brand', 'featured')
    list_filter = ('featured', 'category', 'brand')
    search_fields = ('name', 'description')
    ordering = ('name',)
    list_editable = ('price', 'featured')

@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(ProductSpecification)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_code', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('cart_code',)

admin.site.register(CartItem)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created')
    list_filter = ('rating', 'created')
    search_fields = ('review', 'product__name', 'user__email', 'user__username')
    
@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'average_rating', 'total_reviews')
    search_fields = ('product__name',)
    ordering = ('average_rating',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created')
    list_filter = ('created',)
    ordering = ('user__email', 'user__username', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_code', 'user__email', 'user__username', 'payment_id')
    ordering = ('created_at',)

admin.site.register(OrderItem)