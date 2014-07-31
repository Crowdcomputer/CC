# Django settings for DjangoProjects project.
import os 
import djcelery
djcelery.setup_loader()           

APP_NAME = 'CrowdComputer'
SHORT_APP_NAME = "CC"

DEBUG = True




# Make this unique, and don't share it with anybody.
SECRET_KEY = ''


# app of fb for the login
FACEBOOK_APP_ID = ''
FACEBOOK_API_SECRET = ''



# data for sending emails, check on django docs
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587

MANDRILL_API_KEY = ''
EMAIL_BACKEND = ""

# amz credentials to post on the turk
AMZ_PRIVATE = ''
AMZ_SECRET = ''

# activiti API URL and credential (see activiti rest docs)
ACTIVITI_URL = ""
ACTIVITI_USERNAME=""
ACTIVITI_PASSWORD=""



#location of the source


CM_Location = 'http://localhost:8000'



TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Admin', 'root@localhost'),
)

MANAGERS = ADMINS

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
       'NAME': LOCATION+'sqlite.db',                      # Or path to database file if using sqlite3.
       'USER': '',                      # Not used with sqlite3.
       'PASSWORD': '',                  # Not used with sqlite3.
       'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
       'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
   }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = 'static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"

STATIC_URL = '/static/'


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# List of callables that know how to import as from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    uncomment this for locale
# tutorial:http://devdoodles.wordpress.com/2009/02/14/multi-language-support-in-a-django-project/
#    'django.middleware.locale.LocaleMiddlewar',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'crowdcomputer.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'crowdcomputer.wsgi.application'


TEMPLATE_DIRS = (
        # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        LOCATION + 'general/template',
    )


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.flatpages',
    'django.contrib.markup',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'general',
    'requester',
    'executor',
    'crispy_forms',
    'social_auth',
    'developer',
	'restapi',
#    'bpmn',
    'requests',
    'rest_framework',
    'rest_framework.authtoken',
    'djrill',
    'jsonify',
    'gravatar',
    'djcelery',
    'south',
#    'django-nose',
        
)

# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for

LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format' : "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)s] %(message)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
        },
        'handlers': {
            'null': {
                'level':'DEBUG',
                'class':'django.utils.log.NullHandler',
            },
            'console':{
                'class':'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            'django': {
                'handlers':['console'],
                'propagate': True,
                'level':'WARN',
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'WARN',
                'propagate': False,
            },
            'crowdmachine': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            }, 'executor': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            }, 'general': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            }, 'requester': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'SocialAuth': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'restapi': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
                    'mturk': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
                    'bpmn': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
                    
        }
    }

# AUTH_PROFILE_MODULE = 'earth.UserProfile'

AUTHENTICATION_BACKENDS = (
#    'social_auth.backends.twitter.TwitterBackend',
   'social_auth.backends.facebook.FacebookBackend',
#    'social_auth.backends.google.GoogleOAuthBackend',
#    'social_auth.backends.google.GoogleOAuth2Backend',
#    'social_auth.backends.google.GoogleBackend',
#    'social_auth.backends.yahoo.YahooBackend',
#    'social_auth.backends.browserid.BrowserIDBackend',
#    'social_auth.backends.contrib.linkedin.LinkedinBackend',
#    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
#    'social_auth.backends.contrib.orkut.OrkutBackend',
#    'social_auth.backends.contrib.foursquare.FoursquareBackend',
#    'social_auth.backends.contrib.github.GithubBackend',
#    'social_auth.backends.contrib.vkontakte.VKontakteBackend',
#    'social_auth.backends.contrib.live.LiveBackend',
#    'social_auth.backends.contrib.skyrock.SkyrockBackend',
#    'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
#    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('facebook',)

#TOFILL


    
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'social_auth.context_processors.social_auth_by_type_backends',
    'general.context_processors.addProfile',
    'general.context_processors.addAppName',
    'django.core.context_processors.request',
#    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware', 
)

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    # 'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.user.update_user_details',
    'social_auth.backends.pipeline.social.load_extra_data',
    'general.pipes.get_user_addinfo',
)

FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'user_hometown', 'user_birthday', 'user_location', 'user_likes', 'user_checkins']

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/error/'



REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
#        'rest_framework.authentication.BasicAuthentication',
#        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated', 'restapi.permissions.IsOwnerOrGoOut',
                                               'restapi.permissions.IsFromApp',),
    'PAGINATE_BY': None
    }




ALLOWED_HOSTS = [
    '.crowdcomputer.org',
]

#celery
# BROKER_TRANSPORT = 'sqs'
# BROKER_TRANSPORT_OPTIONS = {
#     'region': 'us-east-1',
# }
# BROKER_USER = AMZ_PRIVATE
# BROKER_PASSWORD = AMZ_SECRET
#
#set it up if  u need it
CELERY=False



                        

