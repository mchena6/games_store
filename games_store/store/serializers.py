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



class CartItemSerializer(serializers.ModelSerializer):
    product = ProductPublicSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    sub_total = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "sub_total"]
        extra_kwargs = {"quantity": {"min_value": 1}}
    # Manejar subtotal del producto
    def get_sub_total(self, item):
        return item.product.price * item.quantity
    
class CartPublicSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializer(many=True, read_only=True)
    total_quantity = serializers.SerializerMethodField()
    cart_total = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Cart
        fields = [
            "id",
            "cart_code",
            "user",
            "cartitems",
            "total_quantity",
            "cart_total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "cart_code", "created_at", "updated_at"]
    # Total de productos
    def get_total_quantity(self, cart):
        return sum(item.quantity for item in cart.cartitems.all())
    # Precio total del carrito
    def get_cart_total(self, cart):
        return sum(item.quantity * item.product.price for item in cart.cartitems.all())
    
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


class OrderPublicItemSerializer(serializers.ModelSerializer):
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
    items = OrderPublicItemSerializer(many=True, read_only=True)

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

class OrderSerializer(serializers.ModelSerializer):
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


class OrderItemSerializer(serializers.ModelSerializer):
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