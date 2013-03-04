mkdir db
touch db/sqlite3.db
python manage.py sql webfrontend
python manage.py syncdb
