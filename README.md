# Item Catalog

Item Catalog is a program that showing items that user creates and managing their own items.
In the application, you can see the items what you and the other users created.
You can create, delete, update your own items. However, you can't delete the other users' items.
In order to create an item, you should have a Google account to login this application.

Install
--------
You should install python2 or python3 in order to run this program, click one of the links provided: [Python2](https://www.python.org/downloads/release/python-2715/) Or [Python3](https://www.python.org/downloads/release/python-372/)

Also you should install VirtualBox and Vagrant, click the links to download: [VirtualBox](https://www.virtualbox.org) and [Vagrant](https://www.vagrantup.com/downloads.html)

After you install the all programs above, you should set up Vagrant with VirtualBox.

The Vagrant configuration file is included within this repository so you can set the environment simply.

Open your terminal and type following codes in the directory where you cloned the repository:
```shell
vagrant up
```
After that type:
```shell
vagrant ssh
```
Then you are ready to run the application.

Running
-------
On your terminal with VM environment, go to the directory that include the files cloned from the repository.

You should run "database_setup.py" to make database
```shell
python database_setup.py
```
If you use python3:
```shell
python3 database_setup.py
```

For testing purpose, "adding_db" file is included. You can populate the database with dummy data using this file. However, this is optional step.

Type the commend to open the server of the program.
```shell
python application.py
```
If you use python3:
```shell
python3 application.py
```

Now, go to your web browser and type "http://localhost:8000/" to access the application.

More Information
----------------
You can see the database as a JSON file by following link below:
Type "http://localhost:8000/catalog.json" to get all catalogs and items db
Or
Type "http://localhost:8000//catalog/<item_name>.json" to get item db

License
-------
Item Catalog is Copyright © 2019 Daewoong Ko.
It is freeware.
