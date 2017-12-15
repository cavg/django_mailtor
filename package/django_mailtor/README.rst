======
mailtor
=====

mailtor is a simple Django app.

Detailed documentation is in the 'docs' directory.

Quick start
-----------

1. Add 'mailtor' to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'mailtor',
    ]

2. Include the mailtor URLconf in your project urls.py like this::

    url(r'^mailtor/', include('mailtor.urls')),

3. Run  to create the mailtor models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/mailtor/.
