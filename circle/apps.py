from django.apps import AppConfig


class CircleConfig(AppConfig):
    name = 'circle'

    def ready(self):
        # suggested by django doc.
        # i guess this is to give application users the choice to whether use the signals or not.
        import circle.signals
