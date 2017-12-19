coverage run --source='.' --omit="manage.py,*/migrations/*,**/urls.py,**/__init__.py,**/settings.py,**/wsgi.py" manage.py test mailtor
coverage report -m