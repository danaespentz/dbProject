# Library Online Management System
This is a project for the Databases class in NTUA Electrical and Computer Engineering Department 

## Contributors
Listed alphabetically:
1. Orestis Karkanis ([orestiskarkanis](https://github.com/orestiskarkanis))
1. Nektarios Mpoumpalos ([nektmpalos](https://github.com/nektmpalos))
1. Danae Spentzou ([danaespentz](https://github.com/danaespentz))

## Tools used
![Python](https://img.shields.io/badge/python-v3.9.2+-red)
![Dependencies](https://img.shields.io/badge/flask-v2.2.3-blue)
![sqlite3](https://img.shields.io/badge/sqlite3-v3.19.3-yellow)

## [Requirements](https://github.com/danaespentz/dbProject/requirements)
- Python 3.9.2
- Flask 2.2.3
- Werkzeug 2.2.3
- Faker==18.5.1

## ER-Diagram

![](https://github.com/danaespentz/dbProject/blob/main/static/ERdiagram.jpg)

## Relational Model

![](https://github.com/danaespentz/dbProject/blob/main/static/relationalDiagram.jpg)

### Download the web-app 

```bash
	$ git clone https://github.com/danaespentz/dbProject
	$ cd dbProject
```
### Download all required libraries

```bash
	$ pip3 install -r requirements.txt
```

### Run the following files to create all sql queries and run the app (at this spesific order !).

- [createdb.py](createdb.py) to create the database and the tables.
- [application.py](application.py) to run the application. 


Open your browser and type <http://127.0.0.1:5000/> to preview the website.

### SQL Queries

Here we show all the [Queries](SQL/) used in the site at each page.
Find the questions for the queries attached to the file [Assignment](Docs/assignment.pdf)



### Disclaimers
- All books where randomly generated by the Faker python Library and any correlation to any real world Books, is purely coincidental.
