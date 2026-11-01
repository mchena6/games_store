import mercadopago
from django.conf import settings
from rest_framework.exceptions import APIException


class MercadoPagoService:
    def __init__(self):
        # Obtener token
        token = getattr(settings, "MERCADOPAGO_ACCESS_TOKEN", None)
        if not token:
            raise APIException("MERCADOPAGO_ACCESS_TOKEN no está configurado.")
        self.sdk = mercadopago.SDK(token)

    # Crear preferencia de pago de cada producto
    def create_preference(self, cart, user):
        items = []
        for item in cart.cartitems.select_related("product").all():
            items.append({
                "id": str(item.product.id),
                "title": item.product.name,
                "quantity": int(item.quantity),
                "currency_id": "ARS", 
                "unit_price": float(item.product.price),
            })

        # Datos de la compra y redireccionamiento
        preference_data = {
            "items": items,
            "payer": {
                "email": user.email,
                "name": user.username,
            },
            "back_urls": {
                "success": f"{settings.FRONTEND_BASE_URL}/checkout/success",
                "failure": f"{settings.FRONTEND_BASE_URL}/checkout/failure",
                "pending": f"{settings.FRONTEND_BASE_URL}/checkout/pending",
            },
            "auto_return": "approved",
            # Guardar cart y user
            "metadata": {
                "user_id": user.id,
                "cart_id": cart.id,
            },
            "notification_url": f"{settings.BACKEND_BASE_URL}/api/checkout/webhook/",
        }

        # Crear preferencia
        preference_response = self.sdk.preference().create(preference_data)
        
        # Validar errores en la respuesta de la API de Mercado Pago
        if preference_response.get("status") not in [200, 201]:
            raise APIException(
                f"Error al comunicarse con Mercado Pago: {preference_response.get('response')}"
            )

        return preference_response["response"]

    def get_payment_info(self, payment_id):
        # Obtener datos del pago desde Mercado Pago
        payment_response = self.sdk.payment().get(payment_id)

        # Error de pago no encontrado
        status_code = payment_response.get("status")
        if status_code == 404:
            return None

        # Errores de Mercado Pago
        if status_code not in [200, 201]:
            raise APIException(
                f"Error al consultar el pago {payment_id}: {payment_response.get('response')}"
            )

        return payment_response["response"]