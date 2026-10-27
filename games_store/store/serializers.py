from rest_framework import serializers
from .models import Category, Brand, Product, Specification, ProductSpecification, Cart, CartItem, Review, ProductRating, Wishlist, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'slug']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'
        read_only_fields = ['id', 'slug']

# Serializer para el GET

class ProductPublicSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'featured', 
            'category', 
            'brand', 
            'slug',
            'image'
        ]
        read_only_fields = ['id', 'slug']


# Serializer para el POST/PUT

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'featured', 
            'category', 
            'brand', 
            'slug',
            'image'
        ]
        read_only_fields = ['id', 'slug']

class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = '__all__'
        read_only_fields = ['id']

class ProductSpecificationPublicSerializer(serializers.ModelSerializer):
    specification = SpecificationSerializer(read_only=True)

    class Meta:
        model = ProductSpecification
        fields = [
            'id', 
            'product', 
            'specification', 
            'value'
        ]
        read_only_fields = ['id']

class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = [
            'id', 
            'product', 
            'specification', 
            'value'
        ]
        read_only_fields = ['id']

# Maneja subtotal de cada producto (cantidad * precio)
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductPublicSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
                'id',
                'product',
                'quantity',
                'sub_total'
                ]

        def get_sub_total(self, cartitem):
            total = cartitem.product.price * cartitem.quantity
            return total

# Maneja el precio total del carrito (suma de todos los subtotales)
class CartSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializer(read_only=True, many=True)
    cart_total = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)    

    def get_cart_total(self, cart):
        items = cart.caritems.all()
        total = 0
        for item in items:
            item_total_price = item.quantity * item.product.price
            total +=  item_total_price
        return total
    class Meta:
        model = Cart
        fields = [
            'id', 
            'cart_code', 
            'user', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

# Maneja la cantidad de productos 
class CartStatSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id','cart_code','cartitems', 'total_quantity']

    def get_total_quantity(self, cart):
        items = cart.cartitems.all()
        total = 0
        for item in items:
            total += item.quantity
        return total

class ReviewPublicSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = ProductPublicSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 
            'user', 
            'product', 
            'rating',
            'review',
            'created',
            'updated'
        ]
        read_only_fields = ['id', 'created', 'updated']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 
            'user', 
            'product', 
            'rating', 
            'review', 
            'created', 
            'updated'
        ]
        read_only_fields = ['id', 'created', 'updated']

class ProductRatingPublicSerializer(serializers.ModelSerializer):
    product = ProductPublicSerializer(read_only=True, many=False)

    class Meta:
        model = ProductRating
        fields = [
            'id', 
            'product', 
            'average_rating', 
            'total_reviews'
        ]
        read_only_fields = ['id']

class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = [
            'id', 
            'product', 
            'average_rating', 
            'total_reviews'
        ]
        read_only_fields = ['id']

class WishlistPublicSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = ProductPublicSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'id', 
            'user', 
            'product', 
            'created'
        ]
        read_only_fields = ['id', 'created']

class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'id', 
            'user',
            'product',
            'created'
        ]
        read_only_fields = ['id', 'created']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductPublicSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'order', 
            'product', 
            'quantity', 
            'price'
        ]
        read_only_fields = ['id']

class OrderPublicSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user', 
            'status', 
            'total_amount', 
            'order_code', 
            'payment_id', 
            'shipping_address', 
            'created_at', 
            'updated_at',
            'items'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = [
#             'id', 
#             'order', 
#             'product', 
#             'quantity', 
#             'price'
#         ]
#         read_only_fields = ['id']