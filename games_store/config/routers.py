from rest_framework.routers import DefaultRouter

from store.views import CategoryViewSet, BrandViewSet, ProductViewSet, SpecificationViewSet, ProductSpecificationViewSet, CartViewSet, CartItemViewSet, ReviewViewSet, ProductRatingViewSet, WishlistViewSet, OrderViewSet, OrderItemViewSet

router = DefaultRouter()

router.register('categories', CategoryViewSet, basename='category_vs')
router.register('brands', BrandViewSet, basename='brand_vs')
router.register('products', ProductViewSet, basename='product_vs')
router.register('specifications', SpecificationViewSet, basename='specification_vs')
router.register('product-specifications', ProductSpecificationViewSet, basename='product_specification_vs')
router.register('carts', CartViewSet, basename='cart_vs')
router.register('cart-items', CartItemViewSet, basename='cart_item_vs')
router.register('reviews', ReviewViewSet, basename='review_vs')
router.register('product-ratings', ProductRatingViewSet, basename='product_rating_vs')
router.register('wishlists', WishlistViewSet, basename='wishlist_vs')
router.register('orders', OrderViewSet, basename='order_vs')
router.register('order-items', OrderItemViewSet, basename='order_item_vs')