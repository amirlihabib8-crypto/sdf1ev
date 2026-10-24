from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Category, Event, User, Registration
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university_events.db'
app.config['SECRET_KEY'] = 'gizli_acar_soz'

db.init_app(app)

with app.app_context():
    db.create_all()


# 1. Ana Səhifə və İdarəetmə Paneli (Dashboard & Statistics)
@app.route('/')
def index():
    total_events = Event.query.count()
    total_registrations = Registration.query.count()
    categories = Category.query.all()

    # Ən çox qeydiyyat olan tədbirlər
    popular_events = db.session.query(Event).join(Registration).group_by(Event.id).order_by(
        db.func.count(Registration.id).desc()).limit(5).all()

    return render_template('index.html',
                           total_events=total_events,
                           total_registrations=total_registrations,
                           categories=categories,
                           popular_events=popular_events)


# 2. Tədbirlərin Siyahısı, Axtarış və Filtrasiya
@app.route('/events')
def events_list():
    query = request.args.get('query', '')
    category_id = request.args.get('category', '')
    location = request.args.get('location', '')

    events_query = Event.query

    if query:
        events_query = events_query.filter(Event.title.ilike(f'%{query}%'))
    if category_id:
        events_query = events_query.filter_by(category_id=category_id)
    if location:
        events_query = events_query.filter(Event.location.ilike(f'%{location}%'))

    events = events_query.all()
    categories = Category.query.all()

    current_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('events.html', events=events, categories=categories, current_date=current_date)


# 3. Yeni Tədbir Yaratmaq
@app.route('/event/new', methods=['GET', 'POST'])
def create_event():
    categories = Category.query.all()

    # Əgər kateqoriya hələ yoxdursa, avtomatik bir neçə kateqoriya əlavə edək
    if not categories:
        default_cats = ['Elmi Konfrans', 'Seminar', 'Təlim', 'Müsabiqə']
        for cat_name in default_cats:
            db.session.add(Category(name=cat_name))
        db.session.commit()
        categories = Category.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        date = request.form.get('date')
        time = request.form.get('time')
        location = request.form.get('location')
        max_participants = request.form.get('max_participants')

        # Məcburi sahələrin yoxlanılması (Validation)
        if not title or not description or not date or not time or not location or not max_participants:
            flash('Bütün sahələri doldurmaq məcburidir!', 'danger')
            return redirect(url_for('create_event'))

        new_event = Event(
            title=title,
            description=description,
            category_id=int(category_id),
            date=date,
            time=time,
            location=location,
            max_participants=int(max_participants)
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Tədbir uğurla yaradıldı!', 'success')
        return redirect(url_for('events_list'))

    return render_template('create_event.html', categories=categories)


# 4. Tədbirə Qeydiyyat
@app.route('/event/<int:event_id>/register', methods=['POST'])
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    name = request.form.get('name')
    email = request.form.get('email')

    if not name or not email:
        flash('Ad və e-poçt daxil edilməlidir!', 'danger')
        return redirect(url_for('events_list'))

    # İstifadəçi bazada varmı yoxla, yoxdursa yarat
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()

    # İştirakçı limitinin yoxlanılması
    current_registrations_count = Registration.query.filter_by(event_id=event.id).count()
    if current_registrations_count >= event.max_participants:
        flash('Tədbirin iştirakçı limiti dolub!', 'danger')
        return redirect(url_for('events_list'))

    # Təkrar qeydiyyatın qarşısının alınması
    existing_reg = Registration.query.filter_by(user_id=user.id, event_id=event.id).first()
    if existing_reg:
        flash('Siz artıq bu tədbirə qeydiyyatdan keçmisiniz!', 'warning')
        return redirect(url_for('events_list'))

    new_reg = Registration(user_id=user.id, event_id=event.id)
    db.session.add(new_reg)
    db.session.commit()
    flash('Tədbirə uğurla qeydiyyatdan keçdiniz!', 'success')
    return redirect(url_for('events_list'))


if __name__ == '__main__':
    app.run(debug=True)