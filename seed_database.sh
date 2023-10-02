   #!/bin/bash

   rm db.sqlite3
   rm -rf ./rockapi/migrations
   python3 manage.py migrate
   python3 manage.py makemigrations rockapi
   python3 manage.py migrate rockapi
   python3 manage.py loaddata types
   python3 manage.py loaddata rocks
