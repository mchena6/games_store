from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django.views.generic import TemplateView

from .models import (
    Category, Brand, Product, Specification, ProductSpecification, Cart, CartItem, Review, ProductRating, Wishlist, Order, OrderItem
)
from .serializers import (
    CategorySerializer, BrandSerializer, SpecificationSerializer, ProductSerializer, ProductPublicSerializer,
    ProductSpecificationSerializer, ProductSpecificationPublicSerializer, CartSerializer,
    CartItemSerializer, ReviewSerializer, ReviewPublicSerializer, ProductRatingSerializer, ProductRatingPublicSerializer,
    WishlistSerializer, WishlistPublicSerializer, OrderPublicSerializer, OrderItemSerializer,
)

# Create your views here.

#PUblico

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "id"]

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "id"]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related("category", "brand").order_by("id")
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = {
        "category": ["exact"],
        "brand": ["exact"],
        "price": ["exact", "gt", "lt", "gte", "lte"],
        "featured": ["exact"],
    }
    search_fields = ["name", "description", "category__name", "brand__name"]
    ordering_fields = ["name", "price", "id"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductPublicSerializer
        else:
            return ProductSerializer

class SpecificationViewSet(viewsets.ModelViewSet):
    queryset = Specification.objects.all().order_by("id")
    serializer_class = SpecificationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProductSpecificationViewSet(viewsets.ModelViewSet):
    queryset = ProductSpecification.objects.all().select_related("product", "specification").order_by("id")
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "product": ["exact"],
        "specification": ["exact"]
    }

    def get_serializer_class(self):
        if self.action == "list":
            return ProductSpecificationPublicSerializer
        else:
            return ProductSpecificationSerializer


# requieren Auth

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"cart_code": ["exact"]}

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related("user").order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return CartPublicSerializer
        else:
            return CartSerializer

    # Se encarga de asignar el usuario al carrito al crearlo
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def vaciar(self, request, pk=None):
        cart = self.get_object()
        cart.cartitems.all().delete()
        return Response({"status": "El carrito ha sido vaciado con éxito"})

class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"cart": ["exact"]}

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
            ).select_related("cart__user", "product__category", "product__brand").order_by("id")

    def get_serializer_class(self):
        if self.action == "list":
            return CartItemPublicSerializer
        else:
            return CartItemSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related("product__category","product__brand", "user").order_by("id")
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "product": ["exact"],
        "rating": ["exact", "gte"]
    }
    ordering_fields = ["rating", "created"]

    def get_serializer_class(self):
        if self.action == "list":
            return ReviewPublicSerializer
        else:
            return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProductRatingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductRating.objects.all().select_related("product__category", "product__brand").order_by("id")
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "product": ["exact"],
        "average_rating": ["exact", "gte"]
    }
    ordering_fields = ["average_rating"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductRatingPublicSerializer
        else:
            return ProductRatingSerializer

class WishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"product": ["exact"]}

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related("product__category", "product__brand", "user").order_by("-created")

    def get_serializer_class(self):
        if self.action == "list":
            return WishlistPublicSerializer
        else:
            return WishlistSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {"status": ["exact"]}
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("user").order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return OrderPublicSerializer
        else:
            return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        order = self.get_object()

        if order.status == 'Pending':
            order.status = 'Canceled'
            order.save()
            return Response({"status": "La orden ha sido cancelada"})
        return Response(
            {"error": "Solo se pueden cancelar órdenes en estado Pending."},
            status=status.HTTP_400_BAD_REQUEST
            )
class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"order": ["exact"]}

    def get_queryset(self):
        return CartItem.objects.filter(
            order__user=self.request.user
            ).select_related("order__user", "product__category", "product__brand").order_by("id")

    def get_serializer_class(self):
        if self.action == "list":
            return OrderItemPublicSerializer
        else:
            return OrderItemSerializer

class WelcomeView(TemplateView):
    template_name = "welcome.html"