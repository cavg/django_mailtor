pip3 uninstall -y django_mailtor &&

cp readme.md package/django_mailtor
cp requirements.txt package/django_mailtor

# Packing new version
cd package/django_mailtor/ &&
python3 setup.py sdist &&

#Install new version
pip3 install --user dist/django_mailtor-0.0.2.tar.gz &&
cd ../../
