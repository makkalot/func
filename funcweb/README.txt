funcweb
=======

A TurboGears interface to func.

This project is currently under development, and is currently just a
proof-of-concept and should not be used in a production environment.

Running
=======

    # yum install TurboGears python-genshi python-elixir
    $ python setup.py egg_info
    $ tg-admin sql create
    # ./start-funcweb.py

Connect to http://localhost:8080

Creating a new user
===================

Currently funcweb only allows connections from 127.0.0.1 and from authenticated
users.  So if you wish to grant other people access to your funcweb instance,
you can create new users easily:

    $ tg-admin shell
    >>> user = User(user_name='name', password='password')
    >>> ^D

Authors
=======
Luke Macken <lmacken@redhat.com>
