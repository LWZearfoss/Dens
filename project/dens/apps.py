from django.apps import AppConfig


class DensConfig(AppConfig):
    name = 'dens'

    def ready(self):
        import dens.models
        dens.models.DenConnectionModel.objects.all().delete()
        import dens.signals
