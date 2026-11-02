import uuid

from django.db import transaction
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django.views.generic import TemplateView

from store.services.mercadopago_service import MercadoPagoService
from users.models import CustomUser

from .models import (
    Category, Brand, Product, Specification, ProductSpecification, Cart, CartItem, Review, ProductRating, Wishlist, Order, OrderItem
)
from .serializers import (
     BrandSerializer, CategorySerializer, SpecificationSerializer, ProductSerializer, ProductPublicSerializer,
     ProductSpecificationSerializer, ProductSpecificationPublicSerializer,
     CartItemSerializer, CartPublicSerializer, ReviewSerializer, ReviewPublicSerializer, ProductRatingSerializer, ProductRatingPublicSerializer,
     WishlistSerializer, WishlistPublicSerializer, OrderPublicItemSerializer, OrderPublicSerializer, OrderItemSerializer, OrderSerializer
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

    def get_queryset(self):
        # Filtrar por usuario logueado y traer los productos del carrito
        items = CartItem.objects.select_related("product__category", "product__brand")
        return (
            Cart.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related(Prefetch("cartitems", queryset=items))
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        return CartPublicSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, cart_code=uuid.uuid4().hex[:30])

    @action(detail=False, methods=["post"], url_path="add-item")
    def add_item(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        # Validar cantidad default de producto > 1
        try:
            quantity = int(quantity)
            if quantity < 1:
                return Response(
                    {"error": "La cantidad debe ser mayor o igual a 1."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Cantidad inválida."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verificar si el producto existe
        product = get_object_or_404(Product, pk=product_id)

        # Buscar carrito asociado al usuario o crear uno si no existe
        cart, _ = Cart.objects.get_or_create(
            user=request.user,
            defaults={"cart_code": uuid.uuid4().hex[:30]},
        )

        # 3. Agrega o incrementa el CartItem respetando la unicidad
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        # Agregar 1 a la cantidad del CartItem si no esta siento creado (producto)
        if not created:
            cart_item.quantity += quantity
            cart_item.save(update_fields=["quantity"])

        # Refrescar el carrito para recalcular totales y subtotales
        cart_refreshed = (
            Cart.objects.filter(pk=cart.pk)
            .prefetch_related(
                Prefetch(
                    "cartitems",
                    queryset=CartItem.objects.select_related("product__category", "product__brand"),
                )
            )
            .first()
        )

        # Devolver responses y serializer
        serializer = CartPublicSerializer(cart_refreshed, context=self.get_serializer_context())
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    # Vaciar carrito
    @action(detail=True, methods=["post"])
    def vaciar(self, request, pk=None):
        # Verificar que existe el carrito y eliminar cartItems
        cart = self.get_object()  
        cart.cartitems.all().delete()
        serializer = CartPublicSerializer(cart, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)


# Permite ver a cualquiera, pero solo el autor puede modificarlo
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        # Filtrar por usuario
        return (
            CartItem.objects.filter(cart__user=self.request.user)
            .select_related("cart", "product__category", "product__brand")
            .order_by("id")
        )

    # Actualizar carrito
    def _get_updated_cart_response(self, cart_id, message=None):
        # Volver a cargar los items del carrito
        items_prefetch = CartItem.objects.select_related("product__category", "product__brand")
        cart = (
            Cart.objects.filter(pk=cart_id)
            .select_related("user")
            .prefetch_related(Prefetch("cartitems", queryset=items_prefetch))
            .first()
        )
        cart_data = CartPublicSerializer(cart, context=self.get_serializer_context()).data

        # Devolver datos del serializer
        response_payload = {
            "cart": cart_data
        }
        if message:
            response_payload["message"] = message

        return Response(response_payload, status=status.HTTP_200_OK)

    # Aumentar cantidad (+1) de un producto en el carrito
    @action(detail=True, methods=["post"], url_path="incrementar")
    def incrementar(self, request, pk=None):
        # Filtrar por usuario
        cart_item = self.get_object()  
        cart_item.quantity += 1
        cart_item.save(update_fields=["quantity"])

        # Actualizar carrito y retornarlo 
        return self._get_updated_cart_response(
            cart_id=cart_item.cart_id,
            message="Cantidad incrementada con éxito."
        )

    # Restar cantidad (-1) de un producto en el carrito
    @action(detail=True, methods=["post"], url_path="decrementar")
    def decrementar(self, request, pk=None):
        # Filtrar por usuario
        cart_item = self.get_object()  
        cart_id = cart_item.cart_id

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save(update_fields=["quantity"])
            msg = "Cantidad decrementada con éxito."
        else:
            # Si la cantidad actual es 1, elimina el CartItem del carrito
            cart_item.delete()
            msg = "El producto fue eliminado del carrito al llegar a cantidad 0."
            
        # Actualizar carrito y retornarlo 
        return self._get_updated_cart_response(cart_id=cart_id, message=msg)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related("product__category","product__brand", "user").order_by("id")
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
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
        if self.action in ["list", "retrieve", "add_product"]:
            return WishlistPublicSerializer
        else:
            return WishlistSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

   # Agregar producto a la Wishlist
    @action(detail=False, methods=["post"], url_path="add-product")
    def add_product(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"error": "El campo 'product_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product = get_object_or_404(Product, pk=product_id)
        # Comprobar si el producto ya existe en la wishlist del usuario logueado
        if Wishlist.objects.filter(user=request.user, product=product).exists():
            return Response(
                {"error": "Este producto ya se encuentra en tu lista de deseos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Agregar producto 
        wishlist_item = Wishlist.objects.create(user=request.user, product=product)
        serializer = WishlistPublicSerializer(wishlist_item, context=self.get_serializer_context())
        return Response(
            {
                "message": "Producto agregado a la lista de deseos con éxito.",
                "item": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    # Eliminar un producto de la Wishlist
    @action(detail=False, methods=["post", "delete"], url_path="remove-product")
    def remove_product(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"error": "El campo 'product_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Comprobar que el producto existe en la Wishlist del usuario logueado
        wishlist_item = Wishlist.objects.filter(user=request.user, product_id=product_id).first()
        if not wishlist_item:
            return Response(
                {"error": "El producto no se encuentra en tu lista de deseos."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Eliminar producto
        wishlist_item.delete()
        return Response(
            {"message": "Producto eliminado de la lista de deseos con éxito."},
            status=status.HTTP_200_OK,
        )


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {"status": ["exact"]}
    ordering_fields = ["created_at", "total_amount"]

    def get_queryset(self):
        return(
            Order.objects.filter(user=self.request.user)            
            .select_related("user")
            .prefetch_related(
                "items__product__category",
                "items__product__brand"
            )
            .order_by("-created_at")
        )

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
        return OrderItem.objects.filter(
            order__user=self.request.user
            ).select_related("order__user", "product__category", "product__brand").order_by("id")

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return OrderPublicItemSerializer
        else:
            return OrderItemSerializer

class WelcomeView(TemplateView):
    template_name = "welcome.html"


class CreatePreferenceView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # Obtener el carrito del usuario logueado
        try:
            cart = Cart.objects.prefetch_related("cartitems__product").get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"error": "No se encontró un carrito activo para este usuario."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Validar que el carrito no este vacio
        if not cart.cartitems.exists():
            return Response(
                {"error": "No se puede realizar la compra: el carrito está vacío."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Crear preferencia en Mercado Pago
        try:
            mp_service = MercadoPagoService()
            preference = mp_service.create_preference(cart, request.user)
        except Exception as e:
            return Response(
                {"error": f"Fallo al conectar con la pasarela de pagos: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        # Devolver links de pago y id de preferencia
        return Response({
            "preference_id": preference.get("id"),
            "init_point": preference.get("init_point"),
            "sandbox_init_point": preference.get("sandbox_init_point"),
        }, status=status.HTTP_201_CREATED)



class MercadoPagoWebhookView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        # Obtener respuesta de cualquier tipo
        topic = request.query_params.get("topic") or request.data.get("type")
        payment_id = request.query_params.get("id") or request.data.get("data", {}).get("id")
        if not payment_id or topic != "payment":
            # Ignorar notificaciones que no sean de tipo 'payment'
            return Response({"status": "ignored"}, status=status.HTTP_200_OK)
        # Consultar informacion del pago en la API de Mercado Pago
        try:
            mp_service = MercadoPagoService()
            payment_info = mp_service.get_payment_info(str(payment_id))
        except Exception as e:
            return Response(
                {"error": f"Error al verificar pago con Mercado Pago: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        # Si el pago no fue encontrado en Mercado Pago
        if not payment_info:
            return Response(
                {"error": f"El pago con ID {payment_id} no existe en Mercado Pago."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Obtener status del pago
        payment_status = payment_info.get("status")
        status_detail = payment_info.get("status_detail")

        # Verificar si este payment_id ya fue procesado
        if Order.objects.filter(payment_id=str(payment_id)).exists():
            return Response(
                {"message": "El pago ya fue procesado con anterioridad."},
                status=status.HTTP_200_OK,
            )
        # Si el pago no fue aprobado
        if payment_status != "approved":
            return Response({
                "message": "Pago no aprobado. No se generó ninguna orden de compra.",
                "payment_id": payment_id,
                "status": payment_status,
                "status_detail": status_detail,  
            }, status=status.HTTP_200_OK)
        # Obtener usuario y carrito
        metadata = payment_info.get("metadata", {})
        user_id = metadata.get("user_id")
        cart_id = metadata.get("cart_id")
        # Buscar usuario y carrito asociados
        try:
            user = CustomUser.objects.get(pk=user_id)
            cart = Cart.objects.prefetch_related("cartitems__product").get(pk=cart_id, user=user)
        except (CustomUser.DoesNotExist, Cart.DoesNotExist):
            return Response(
                {"error": "Usuario o Carrito asociado al pago no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Crear Order, congelar OrderItems y vaciar el Carrito
        with transaction.atomic():
            # Crear Order
            total_amount = payment_info.get("transaction_amount", 0.00)
            order_code = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            order = Order.objects.create(
                user=user,
                order_code=order_code,
                total_amount=total_amount,
                status="Paid",
                payment_id=str(payment_id),
                shipping_address=payment_info.get("payer", {}).get("address", {}).get("street_name") or "No especificada"
            )
            # Guardar OrderItems en la orden de compra
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )
                for item in cart.cartitems.all()
            ]
            OrderItem.objects.bulk_create(order_items)
            # Vaciar el carrito de compra
            cart.cartitems.all().delete()
        # Devolver datos de la orden
        serializer = OrderPublicSerializer(order)
        return Response({
            "message": "Pago aprobado con éxito. Orden de compra creada.",
            "order": serializer.data
        }, status=status.HTTP_201_CREATED)
