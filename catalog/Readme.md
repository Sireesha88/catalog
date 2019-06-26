# Book Store
### By Sai Sireesha Pendyala
This is one of the project in the Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

# Project Overview
It is a book store web app where any user can view the details of the item but only the authenticated people can add, edit, and delete book items and their categories based on the availability.

### Why This Project?
This web application is more useful for the users.Mohttp://localhost:5000/items/JSONdern web applications perform a variety of functions and provide amazing features and utilities to their users; but deep down, it’s really all just creating, reading, updating and deleting data. In this project, you’ll combine your knowledge of building dynamic websites with persistent data storage to create a web application that provides a compelling service to your users.

### What Will I Learn?
  * Through this we will develop RESTful web application using the Python framework Flask.
  * Implemention of Login using third-party OAuth authentication.
  * Implementing CRUD (create, read, update and delete) operations on favourite database.

## Skills Required
1. Python
2. HTML
3. CSS
4. OAuth
5. Flask Framework
6. flask_sqlalchemy

### Prerequisites
* Python 
* Vagrant
* VirtualBox

### Project Setup
1. Install VirtualBox and Vagrant
2. Clone this repo
3. Unzip and place the Item Catalog folder in your Vagrant directory
4. Launch Vagrant


#### How to Run
  1. open git bash from vagrant folder
  2. Launch the Vagrant by using the command:
  `
    $ vagrant up
  `
  3. Log into Vagrant by using the command:
  `
    $ vagrant ssh
  `
  4. Move to server side vagrant folder by using the commmand:
  `
    $ cd /vagrant
  `
  5. Move to Project folder ie BookStore by using the command:
  `
    $ cd BookStore
  `
  6. Run the project by using the command:
  `
    $ python bigproject11.py
  `
  7. open our application by visiting from your favourite browser[http://localhost:5000/home](http://localhost:5000/home).
  ### JSON end points
  in this application we created json end points for multi purpose using REST architecture 
#### urls:
`
http://localhost:5000/books/JSON
`
`
http://localhost:5000/categories/JSON
`



