coverage run --source='.' --omit="manage.py,*/migrations/*,**/urls.py,**/__init__.py,**/settings.py,**/wsgi.py,**/local.py,**/production.py,**/apps.py" manage.py test mailtor
coverage report -m