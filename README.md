# audiobook

## setup via vagrant

To start a project, run the following commands:

    vagrant up
    vagrant ssh
    cd /home/vagrant/audiobook
    python3 manage.py createsuperuser
    python3 manage.py runserver 0.0.0.0:8000