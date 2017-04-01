#!/bin/bash

PROJECT_NAME=$1

DB_NAME="${2:-$PROJECT_NAME}"
DB_USER="${3:-$PROJECT_NAME}"
DB_PASSWORD="${4:-$PROJECT_NAME}"

VIRTUALENV_NAME="$PROJECT_NAME"

PROJECT_DIR="/home/vagrant/$PROJECT_NAME"

apt-get update -y

apt-get install -y git build-essential python python3 python3-setuptools python3-dev virtualenv python3-libtorrent

# Postgresql
if ! command -v psql; then
    apt-get install -y postgresql libpq-dev
    # Create vagrant pgsql superuser
#    su - postgres -c "createuser -s ${DB_USER}"
fi

cat << EOF | su - postgres -c psql
-- Create the database user:
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create the database:
CREATE DATABASE $DB_NAME WITH OWNER=$DB_USER
                              LC_COLLATE='en_US.utf8'
                              LC_CTYPE='en_US.utf8'
                              ENCODING='UTF8'
                              TEMPLATE=template0;
EOF

echo "host    all             all             all                     md5" >> /etc/postgresql/*/main/pg_hba.conf
service postgresql restart

if ! command -v pip3; then
    easy_install3 -U pip
fi

if [[ ! -f /usr/local/bin/virtualenv ]]; then
    pip3 install virtualenv virtualenvwrapper stevedore virtualenv-clone
fi

#su - vagrant -c "createdb $DB_NAME"

#chmod a+x "$PROJECT_DIR/manage.py"

cd "$PROJECT_DIR"
pip3 install -r "requirements.txt"
python3 manage.py migrate
