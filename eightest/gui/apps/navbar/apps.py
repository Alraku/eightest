from django.apps import AppConfig


class NavbarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gui.apps.navbar'

    def ready(self):
        print('xd')
