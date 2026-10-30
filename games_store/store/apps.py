from django.apps import AppConfig


class StoreConfig(AppConfig):
    name = "store"

    def ready(self):
        # Registrar los receivers
        import store.signals