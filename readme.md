# Vehicle Parking Management System - V1



A web-based parking management application built using Flask, SQLAlchemy, and SQLite.

The system allows users to register, log in, reserve parking spots, and track parking history.

Admins can manage parking lots, monitor spot availability, and analyze usage trends with built-in visualization tools.



## Features



🔐 User Authentication – Register, login, secure password storage with hashing



🅿️ Parking Lot \& Spot Management – Manage multiple lots and individual spots



📅 Reservations – Reserve and release parking spots in real time



📊 Parking History – Track and view parking usage history



📈 Analytics Dashboard – View graphs and statistics of parking usage (powered by Matplotlib)



🗄 Database – SQLite for lightweight local storage (can be upgraded to PostgreSQL/MySQL)



### Tech Stack



Backend: Flask (Python)



Database ORM: SQLAlchemy



Database: SQLite



Visualization: Matplotlib



Frontend: Jinja2 templates, HTML, CSS



#### 📂 Project Structure

project/

│── app.py                # Main Flask app

│── models.py             # Database models

│── templates/            # HTML templates

│── static/               # CSS, JS, images

│── instance/             # SQLite database file

│── requirements.txt      # Dependencies

│── README.md             # Project documentation



##### ⚡ Installation \& Setup



**Clone the repository**



git clone https://github.com/SAI-69/Vehicle-Parking-Management-System---V1

cd Vehicle-Parking-Management-System---V1





**Create and activate a virtual environment**



python -m venv venv

source venv/bin/activate   # On Linux/Mac

venv\\Scripts\\activate      # On Windows





**Install dependencies**



pip install -r requirements.txt





**Set up the database**



python

>>> from app import db

>>> db.create\_all()

>>> exit()





**Run the application**



flask run





Open the app in your browser → http://127.0.0.1:5000/



📊 Usage



User: Register, login, reserve a spot, check history.



Admin: Manage lots \& spots, monitor usage, view reports.





📌 Requirements



See requirements.txt

.



**Main packages:**



Flask



Flask-SQLAlchemy



Werkzeug



Matplotlib



SQLAlchemy




