# Biblioteca MariCarmen Brito

Software per a gestió de biblioteques.

En record de Mari Carmen Brito de l'Institut Esteve Terradas i Illa de Cornellà de Llobregat.

## Instal·lació

Instal·leu git, Python3 i l'entorn de treball virtualenv:

    sudo apt update
    sudo apt install python3-venv git

Cloneu el repositori:

    git clone https://github.com/AWS2/biblioteca-maricarmen
    cd biblioteca-maricarmen

Creem el virtualenv i carreguem les biblioteques:

    python3 -m venv env
    source env/bin/activate

Carreguem les biblioteques del sistema (en particular per l'us de MySQL). Pel cas de Debian/Ubuntu:

    sudo apt install libmysqlclient-dev python3-dev python3-mysqldb gcc pkgconf

Carreguem les biblioteques de Python:

    (env) $ pip install -r requirements.txt

Creem la base de dades de desenvolupament i afegim un superusuari:

    (env) $ cp .env.example .env
    (env) $ ./manage.py migrate
    (env) $ ./manage.py createsuperuser

Posem en marxa el servidor de desenvolupament:

    (env) $ ./manage.py runserver

Podeu accedir el servidor a http://localhost:8000/admin/

Per carregar la base de dades de test:

    (env) $ ./manage.py loaddata testdb.json


## Frontend React

Si accedim al frontend http://localhost:8000/ mostrarà un missatge de benvinguda i prou. Si volem activar el frontend realitzat en React caldrà carregar el submòdul a /react i desplegar-ho dins el projecte Django:

    $ git submodule init
    $ git submodule update
    $ ./deploy-react.sh

Ara ja es podrà accedir a la pàgina principal http://localhost:8000/ i visualitzar el frontend complert:

    (env) $ ./manage.py runserver


## API

Per accedir l'API dels llibres cal aconseguir un token vàlid:

GET /api/token
paràmetres:
  * user
  * password

Exemples:
    curl "localhost:8000/api/token/" -i -X GET -u admin:admin123


GET /api/llibres
paràmetres: no n'hi ha

