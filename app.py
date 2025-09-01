from flask import Flask, render_template, redirect, request, url_for, session, flash
from models import db, User, Parking_lot, Parking_spot, Reserve_parking_spot, ParkingHistory
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from collections import Counter,defaultdict
from sqlalchemy import func
import io
from io import BytesIO
import base64
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Niceee'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'


db.init_app(app) #connecting with app and db orm 
  
#Database initialization
with app.app_context():
    db.create_all()

def admin_data():
    with app.app_context():
        admin = User.query.filter_by(full_name='admin1').first()
        if not admin:
            new_admin = User(full_name='admin1',
                             email='xyz@gmail.com',
                             phone_no=1234567890,
                             password=generate_password_hash('admin123'),
                             role='admin')
            db.session.add(new_admin)
            db.session.commit()

def plot_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user_register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phonenumber = request.form['phone']
        password = request.form['password']
        role = request.form.get('role', 'user')

        new_user = User(full_name=full_name, 
                        email=email, 
                        phone_no=phonenumber, 
                        password=generate_password_hash(password), 
                        role=role)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User registered successfully!', 'success')
            return redirect(url_for('user_login'))

        except IntegrityError:
            db.session.rollback() 
            flash('Email, phone number, or password already exists. Please try again.', 'error')
            return render_template('user_register.html')

        # db.session.add(new_user)
        # db.session.commit()
        # flash('User registered successfully!')
        # return redirect(url_for('user_login'))
    return render_template('user_register.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('user_page')) #User_dashborad
        else:
            flash('Invalid email or password!')

    return render_template('user_login.html')

@app.route('/admin_page', methods=['GET', 'POST'])
def admin_page():
    users = User.query.all()
    lots = Parking_lot.query.all()
    
    # Dictionary where each user.id maps to a list of active reservations
    user_status = defaultdict(list)
    for user in users:
        reservations = Reserve_parking_spot.query.filter_by(user_id=user.id).all()

        for res in reservations:
            user_status[user.id].append({
                "lot": res.rel_to_parking_spot.rel_to_parking_lot.location,
                "spot_id": res.spot_id,
                "car_type": res.car_type,
                "vehicle_no": res.vehicle_no
            })


    # Lot summaries
    lot_summaries = []
    for lot in lots:
        occupied=0
        available=0
        for spot in lot.spots:
            if spot.status == 'Occupied':
                occupied += 1
            elif spot.status == 'Available':
                available += 1
        lot_summaries.append({
            'lot': lot,
            'occupied': occupied,
            'available': available
        })
    

    history_by_user = {}
    for user in users:
        history = ParkingHistory.query.filter_by(user_id=user.id).order_by(ParkingHistory.in_time.desc()).all()
        history_by_user[user.id] = history

    return render_template('admin_page.html', Users=users, Parking_lots=lots,
                        lot_summaries=lot_summaries, user_status=user_status,
                        history_by_user=history_by_user,)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('admin_page'))   
        else:
            flash('Invalid email or password!')
    return render_template('admin_login.html')

@app.route('/admin/summary')
def admin_summary():
    # 1. Occupancy Overview
    total_occupied = db.session.query(Parking_spot).filter_by(status='Occupied').count()
    total_available = db.session.query(Parking_spot).filter_by(status='Available').count()

    fig1, ax1 = plt.subplots()
    ax1.pie(
        [total_occupied, total_available],
        labels=['Occupied', 'Available'],
        autopct='%1.1f%%',
        colors=["#de2f2f", "#0AEE0AEC"]
    )
    ax1.set_title('Overall Occupancy')
    occupancy_chart = plot_to_base64(fig1)

    # 2. Parking Spots by Lot
    lots = db.session.query(Parking_lot).all()
    lot_names=[]
    for lot in lots:
        lot_names.append(lot.location)
    occupied=[]
    for lot in lots:
        occupied.append(db.session.query(Parking_spot).filter_by(lot_id=lot.id, status='Occupied').count())
    available=[]
    for lot in lots:
        available.append(db.session.query(Parking_spot).filter_by(lot_id=lot.id, status='Available').count())
    fig2, ax2 = plt.subplots()
    x = range(len(lot_names))
    ax2.bar(x, occupied, label='Occupied', color="#de2f2f")
    ax2.bar(x, available, bottom=occupied, label='Available', color='#0AEE0AEC')
    ax2.set_xticks(x)
    ax2.set_xticklabels(lot_names, rotation=45, ha='right')
    ax2.set_title('Parking Spots by Lot')
    ax2.legend()
    bar_chart = plot_to_base64(fig2)

    # 3. Top 5 Most Active Users
    top_users = (
        db.session.query(User.full_name, func.count(ParkingHistory.id))
        .join(ParkingHistory)
        .group_by(User.id)
        .order_by(func.count(ParkingHistory.id).desc())
        .limit(5)
        .all()
    )


    user_names=[]
    for user in reversed(top_users):
        user_names.append(user[0])
    reservation_counts=[]
    for user in reversed(top_users):
        reservation_counts.append(user[1])

    fig3, ax3 = plt.subplots()
    ax3.barh(user_names, reservation_counts, color='#1d3557')
    ax3.set_title('Top 5 Most Active Users')
    top_users_chart = plot_to_base64(fig3)

    return render_template(
        'admin_summary.html',
        occupancy_chart=occupancy_chart,
        bar_chart=bar_chart,
        top_users_chart=top_users_chart
    )

@app.route('/create_parking_lot', methods=['GET', 'POST']) 
def create_parking_lot():
    if request.method == 'POST':
        location= request.form['location']
        price= request.form['price']
        address= request.form['address']
        pin_code= request.form['pin_code']
        max_spots= request.form['max_spots']
        uni_code = request.form['uni_code']
        new_lot = Parking_lot(location=location, 
                              price=price, 
                              address=address, 
                              pin_code=pin_code, 
                              max_spots=max_spots,
                              unique_lot_code=uni_code)
        db.session.add(new_lot)
        db.session.commit()
        flash('Parking lot created successfully!')
        for _ in range(int(max_spots)):
            spot = Parking_spot(lot_id=new_lot.id, status='Available')
            db.session.add(spot)
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template('admin_page.html')

@app.route('/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    lot = Parking_lot.query.get_or_404(lot_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    # Authorization check
    if not user or (user.role != 'admin' and Parking_lot.user_id != user_id):
        flash("You are not authorized to delete this parking lot.")
        return redirect(url_for('home'))

    # Check if any spots are not available
    occupied_or_reserved_spots=[]
    for spot in lot.spots:
        if spot.status != 'Available':
            occupied_or_reserved_spots.append(spot)
    
    if occupied_or_reserved_spots:
        flash("Cannot delete parking spots/spot are occupied.")
        return redirect(url_for('admin_page'))

    # Deleting associated spots first
    for spot in lot.spots:
        db.session.delete(spot)

    # Deleting the parking lot
    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted successfully.")
    return redirect(url_for('admin_page'))

@app.route('/edit_parking_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = Parking_lot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.location = request.form['location']
        lot.price = request.form['price']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.max_spots = request.form['max_spots']
        lot.unique_lot_code = request.form['uni_code']
        new_max = int(request.form['max_spots'])
        current_spots = len(lot.spots)

        if new_max > current_spots:
            for _ in range(new_max - current_spots):
                new_spot = Parking_spot(lot_id=lot.id, status='Available')
                db.session.add(new_spot)
        elif new_max < current_spots:
            removable_spots = []
            for spot in lot.spots:
                if spot.status != 'Occupied':
                    removable_spots.append(spot)
            to_remove = new_max - current_spots
            for spot in removable_spots[:abs(to_remove)]:
                db.session.delete(spot)
        db.session.commit()
        return redirect(url_for('admin_page'))
    return render_template('edit_lot.html', lot=lot)

@app.route('/manage_spot/<int:spot_id>')
def manage_spot(spot_id):
    spot = Parking_spot.query.get_or_404(spot_id)
    lot = spot.rel_to_parking_lot
    
    if spot.reserve_spot:
        reservation= spot.reserve_spot[0]
    else:
        reservation = None
    if reservation:
        user=reservation.user_rel
    else:   
        user = None
    
    return render_template('manage_spot.html', spot=spot, lot=lot, reservation=reservation, user=user)

@app.route('/release_spot', methods=['POST'])
def release_spot():
    reservation_id = request.form['reservation_id']
    reservation = Reserve_parking_spot.query.get(reservation_id)

    if not reservation:
        flash("Reservation not found.")
        return redirect(url_for('user_page'))

    if session.get('user_id') != reservation.user_id:
        flash("You are not authorized to release this spot.")
        return redirect(url_for('user_page'))

    spot = Parking_spot.query.get(reservation.spot_id)
    if spot:
        spot.status = "Available"

    in_time = reservation.in_time
    actual_out_time = datetime.now()
    duration_hours = (actual_out_time - in_time).total_seconds() / 3600
    lot = Parking_lot.query.join(Parking_spot).filter(Parking_spot.id == reservation.spot_id).first()
    parking_cost = int(duration_hours * lot.price)

    parking_history = ParkingHistory(
        user_id=reservation.user_id,
        spot_id=reservation.spot_id,
        in_time=in_time,
        out_time = datetime.now(),
        parking_cost=parking_cost,
        car_type=reservation.car_type,
        vehicle_no=reservation.vehicle_no,
        lot_name=lot.location
    )
    db.session.add(parking_history)
    db.session.delete(reservation)
    db.session.commit()

    flash(f"Parking spot released successfully. Final cost: ₹{parking_cost}")
    return redirect(url_for('user_page'))

@app.route('/reserve_spot', methods=['POST'])
def reserve_spot():
    lot_id = int(request.form['parking_lot'])
    car_type = request.form['car_type']
    vehicle_no = request.form['vehicle_no']
    in_time = datetime.strptime(request.form['in_time'], '%Y-%m-%dT%H:%M')
    out_time = datetime.strptime(request.form['out_time'], '%Y-%m-%dT%H:%M')
    user_id = session.get('user_id')

    if not user_id:
        flash('Login to reserve a spot.')
        return redirect(url_for('user_login'))

    lot = db.session.get(Parking_lot, lot_id)
    available_spots=[]
    for spot in lot.spots:
        if spot.status == "Available":
            available_spots.append(spot)
    if not available_spots:
        flash('No available parking spots in this lot.')
        return redirect(url_for('user_page'))

    chosen_spot = random.choice(available_spots)
    chosen_spot.status = 'Occupied'

    duration_hours = (out_time - in_time).total_seconds() / 3600
    parking_cost = int(duration_hours * lot.price)
    reservation = Reserve_parking_spot(
        spot_id=chosen_spot.id,
        user_id=user_id,
        in_time=in_time,
        out_time=out_time,
        parking_cost=parking_cost,
        car_type=car_type,
        vehicle_no=vehicle_no
    )
    db.session.add(reservation)
    db.session.commit()

    flash(f"Spot reserved successfully! Spot ID: {chosen_spot.id}")
    return redirect(url_for('user_page'))

@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    lots = Parking_lot.query.all()
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    reservations = Reserve_parking_spot.query.filter_by(user_id=user_id).order_by(Reserve_parking_spot.in_time.desc()).all()
    history = ParkingHistory.query.filter_by(user_id=user_id).order_by(ParkingHistory.in_time.desc()).all()

    reservations_history=ParkingHistory.query.filter_by(user_id=user_id).order_by(ParkingHistory.in_time.desc()).all() #newline

    date_counts = defaultdict(int)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    his_date_counts=defaultdict(int) 

    for hres in reservations_history: 
        his_date_str = hres.in_time.strftime('%Y-%m-%d') 
        his_date_counts[his_date_str] += 1 
    approx_reservations = []
    for res in reservations:
        date_str = res.in_time.strftime('%Y-%m-%d')
        date_counts[date_str] += 1

        lot = Parking_lot.query.join(Parking_spot).filter(Parking_spot.id == res.spot_id).first()
        duration_hours = (res.out_time - res.in_time).total_seconds() / 3600
        res.approx_cost = int(duration_hours * lot.price)
        approx_reservations.append(res)

    sorted_dates = sorted(date_counts.items())
    dates=[]
    counts=[]
    for x in sorted_dates:
        dates.append(x[0])
        counts.append(x[1])
    his_sorted_dates = sorted(his_date_counts.items()) 
    his_dates=[] 
    his_counts=[] 
    for y in his_sorted_dates: 
        his_dates.append(y[0]) 
        his_counts.append(y[1]) 

    his_chart_data = None #newline
    if his_dates and his_counts:
        plt.figure(figsize=(8, 4))
        plt.bar(his_dates, his_counts,  color='blue')
        plt.xticks(rotation=45, ha='right')
        plt.title("Your Reservations History Over Time")
        plt.xlabel("Date")
        plt.ylabel("Reservations")
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        his_chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
    return render_template('user_page.html', Parking_lots=lots, user=user, reservations=approx_reservations, chart_data=his_chart_data, history=history, current_time=current_time)

@app.route('/logout', methods=['GET','POST'])
def logout():
    session.clear() 
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('home'))

@app.route('/*', methods=['GET'])
def not_found(e):
    return render_template('404.html'), 404
#------------------------------ Not required functionality  -----------------------------
@app.route('/delete_spot/<int:spot_id>', methods=['POST'])
def delete_spot(spot_id):
    spot = Parking_spot.query.get_or_404(spot_id)

    if spot.status != 'Available':
        flash("Cannot delete: the spot is currently occupied.")
        return redirect(url_for('manage_spot', spot_id=spot.id))

    db.session.delete(spot)
    db.session.commit()
    flash("Spot deleted successfully.")
    return redirect(url_for('admin_page'))

if __name__ == '__main__':
    admin_data()
    app.run(debug= True, port = 5000) 
    
