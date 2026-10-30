# store/signals.py

from django.db.models import Avg, Count
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Review, ProductRating


# Se ejecuta cuando se crea un producto
@receiver(post_save, sender=Product)
def create_product_rating(sender, instance, created, **kwargs):
    # Crear Product Rating
    if created:
        ProductRating.objects.get_or_create(
            product=instance,
            defaults={"average_rating": 0.0, "total_reviews": 0}
        )


# Se ejecuta al agregar, modificar, editar o eliminar una Review:
@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product

    # Obtener o crear Product Rating
    product_rating, _ = ProductRating.objects.get_or_create(
        product=product,
        defaults={"average_rating": 0.0, "total_reviews": 0}
    )

    # Calcular total de reviews y promedio de Rating
    stats = product.reviews.aggregate(
        total=Count("id"),
        avg_rating=Avg("rating")
    )

    total_reviews = stats["total"] or 0
    average_rating = round(stats["avg_rating"], 2) if stats["avg_rating"] is not None else 0.0

    # Actualizar total de reviews y Rating
    product_rating.total_reviews = total_reviews
    product_rating.average_rating = average_rating
    product_rating.save(update_fields=["total_reviews", "average_rating"])