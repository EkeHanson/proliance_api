from django.apps import AppConfig


class IssuesLogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'issues_log'

    def ready(self):
        import issues_log.signals  # Import signals to connect them
