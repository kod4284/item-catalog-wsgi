# item-catalog-wsgi
-------------------
Linux Sever Configuration for Item Catalog application I have made before [Item Catalog](https://github.com/kodw0402/item-catalog)

The Item Catalog application is now running on the Linux sever on the Apache2 environment.

Visit http://daewoongko.ga to see it.

If the link doesn't work, try http://50.17.107.48.xip.io


Server Information
------------------
public IP Address: 50.17.107.48
private key(grader) is not provided here

Open ports are:
* SSH Port: 2200
* HTTP: 80
* NTP: 123
```
To                         Action      From
--                         ------      ----
2200                       ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
123                        ALLOW       Anywhere
2200 (v6)                  ALLOW       Anywhere (v6)
80/tcp (v6)                ALLOW       Anywhere (v6)
123 (v6)                   ALLOW       Anywhere (v6)
```

Instruction to SSH
------------------
Download the private key and locate it under your path `~/.ssh/`

Open a terminal window and type:
```shell
ssh grader@50.17.107.48 -p 2200 -i ~/.ssh/grader
```

Add a new user
--------------
After login-in via the terminal, type:
```shell
sudo adduser <new username>
sudo touch /etc/sudoers.d/<new username>
sudo nano /etc/sudoers.d/<new username>
```
And on the nano widow, type:
```shell
<new username> ALL=(ALL:ALL) ALL
```
type CTRL+X, 'y' and ENTER to save and exit

making new ssh key by using ssh-keygen
--------------------------------------
On the client computer, open terminal and type:
```shell
ssh-keygen
```
By following the step, you can generate private and public key in the path ~/.ssh

Now you should copy the value of key into the server.

On your server side terminal, type
```shell
sudo nano .ssh/authorized_keys
```
Copy the public key value into this and save

Give permission by typing
```shell
chmod 700 .ssh
chmod 644 .ssh/authorized_keys
```

Keep the sever up-to-date
-------------------------
```shell
sudo apt-get update
sudo apt-get upgrade
```

Change the SSH port from 22 to 2200
-----------------------------------
```shell
sudo ufw allow 2200
sudo ufw allow 80
sudo ufw allow 123
sudo ufw enable
```

Install Apache2 and mod_wsgi to run Python Flask application
------------------------------------------------------------

```shell
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi-py3
sudo apache2ctl restart
```

Install git
-----------
```shell
sudo apt-get install git
```

Install PostgreSQL and set up DB and user
----------------------------------
```shell
sudo apt-get install postgresql
sudo -u postgres createdb <dbname>
sudo -u postgres createuser <username>
sudo -u postgres psql
psql=# alter user <username> with encrypted password '<password>';
psql=# grant all privileges on database <dbname> to <username> ;
```

Edit Apache .conf file
----------------------
```
<VirtualHost *:80>
DocumentRoot /var/www/html
WSGIScriptAlias / /var/www/html/app.wsgi
        <Directory /var/www/html/>
            Order allow,deny
            Allow from all
         </Directory>
</VirtualHost>

```


Create the .wsgi File
---------------------
```
import sys
sys.path.insert(0, '/var/www/html/')
from __init__ import app as application
application.secret_key = 'super_secret_key'
```

License
-------
Item Catalog is Copyright © 2019 Daewoong Ko.
It is freeware.
