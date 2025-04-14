from django.apps import AppConfig


class InfraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infra'

class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import infra.signals

class YourAppConfig(AppConfig):
    name = 'infra'

    def ready(self):
        import infra.signals 
