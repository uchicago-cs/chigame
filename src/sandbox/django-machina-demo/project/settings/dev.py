from .base import *  # noqa

# APP CONFIGURATION
# ------------------------------------------------------------------------------

INSTALLED_APPS += ("debug_toolbar",)  # noqa: F405


# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------

MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)  # noqa: F405


# DEBUG CONFIGURATION
# ------------------------------------------------------------------------------

DEBUG = True


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]
INTERNAL_IPS = [
    "127.0.0.1",
]


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------

TEMPLATES[0]["OPTIONS"]["loaders"] = (  # noqa: F405
    # Disables cached loader
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)


# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------

STATICFILES_DIRS = (
    MACHINA_MAIN_STATIC_DIR,  # noqa: F405
    str(PROJECT_PATH / "main" / "static"),  # noqa: F405
)

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
