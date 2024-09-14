from django.apps import AppConfig


class ServiceConfig(AppConfig):
	default_auto_field: str = 'django.db.models.BigAutoField'
	name: str = 'app'
