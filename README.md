A simple Flask application that will handle basic management of an ISC DHCPD server. At the moment it does not do much, but it will grow over time.

On the server running dhcpd, start dhcpd-flask:

```
python dhcpd-flask.py
```

On a client:

To retrieve all host reservations

````
python dhcpd-flask-client.py --get
```

To add a host reservation entry

```
python dhcpd-flask-client.py --add --host somename --mac ff:ff:ff:ff:ff:ff --ip 127.0.0.1
```

This is a simple self-starter/learn Python project for myself with some pratical use in my personal lab environment.
