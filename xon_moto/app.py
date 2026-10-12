import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
import database

app = Flask(__name__)
app.secret_key = 'xon_moto_secret_super_key_2026'

# Fayl yuklash konfiguratsiyasi
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'avif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ma'lumotlar bazasini ishga tushirish
database.init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Jinja uchun filterlar
@app.template_filter('format_price')
def format_price(value):
    try:
        val = int(value)
        return f"{val:,}".replace(",", " ")
    except (ValueError, TypeError):
        return value

@app.template_filter('price_in_som')
def price_in_som(usd_value, rate=12850):
    try:
        val = int(usd_value) * rate
        return f"{val:,}".replace(",", " ")
    except (ValueError, TypeError):
        return "0"

@app.route('/')
def index():
    stats = database.get_stats()
    # Tanlangan VIP mashinalar
    featured_vehicles = database.get_vehicles(sort_by='popular', limit=6)
    # Hamyonbop mashinalar
    budget_vehicles = database.get_vehicles(category='budget', limit=4)
    # Qimmatbaho mashinalar
    luxury_vehicles = database.get_vehicles(category='luxury', limit=4)
    # Mototsikllar
    moto_vehicles = database.get_vehicles(category='moto', limit=4)

    return render_template(
        'index.html',
        stats=stats,
        featured_vehicles=featured_vehicles,
        budget_vehicles=budget_vehicles,
        luxury_vehicles=luxury_vehicles,
        moto_vehicles=moto_vehicles
    )

@app.route('/catalog')
def catalog():
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    sort_by = request.args.get('sort_by', 'newest')

    vehicles = database.get_vehicles(
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by
    )

    stats = database.get_stats()

    return render_template(
        'catalog.html',
        vehicles=vehicles,
        current_category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        stats=stats,
        total_found=len(vehicles)
    )

@app.route('/vehicle/<int:vehicle_id>')
def vehicle_detail(vehicle_id):
    vehicle = database.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        flash("Kechirasiz, bunday transport vositasi topilmadi.", "danger")
        return redirect(url_for('catalog'))

    # O'xshash transport vositalari
    similar = database.get_vehicles(category=vehicle['category'], limit=4)
    similar = [v for v in similar if v['id'] != vehicle['id']][:3]

    return render_template('detail.html', vehicle=vehicle, similar=similar)

@app.route('/add-listing', methods=['GET', 'POST'])
def add_listing():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'budget')
        brand = request.form.get('brand', '').strip()
        model = request.form.get('model', '').strip()
        year = request.form.get('year', 2024)
        price = request.form.get('price', 0)
        mileage = request.form.get('mileage', 0)
        engine = request.form.get('engine', '').strip()
        fuel_type = request.form.get('fuel_type', 'Benzin')
        transmission = request.form.get('transmission', 'Avtomat')
        drive_type = request.form.get('drive_type', 'Oldi')
        color = request.form.get('color', '').strip()
        body_type = request.form.get('body_type', 'Sedan')
        description = request.form.get('description', '').strip()
        seller_name = request.form.get('seller_name', '').strip()
        seller_phone = request.form.get('seller_phone', '').strip()
        seller_telegram = request.form.get('seller_telegram', '').strip()
        city = request.form.get('city', 'Toshkent shahri')
        image_url = request.form.get('image_url', '').strip()

        # Fayl yuklanganmi?
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex[:12]}.{ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image_url = url_for('static', filename=f'uploads/{unique_filename}')

        # Agar rasm berilmagan bo'lsa, standart rasm qo'yish
        if not image_url:
            if category == 'moto':
                image_url = "https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=1200&q=80"
            elif category == 'luxury':
                image_url = "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80"
            else:
                image_url = "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=1200&q=80"

        # Sarlavhani avtomatik to'ldirish
        if not title:
            title = f"{brand} {model} {year}"

        new_vehicle_id = database.add_vehicle({
            'title': title,
            'category': category,
            'brand': brand,
            'model': model,
            'year': int(year) if str(year).isdigit() else 2024,
            'price': int(price) if str(price).isdigit() else 0,
            'mileage': int(mileage) if str(mileage).isdigit() else 0,
            'engine': engine or 'Standart',
            'fuel_type': fuel_type,
            'transmission': transmission,
            'drive_type': drive_type,
            'color': color or 'Oq',
            'body_type': body_type,
            'description': description,
            'image_url': image_url,
            'additional_images': [],
            'seller_name': seller_name,
            'seller_phone': seller_phone,
            'seller_telegram': seller_telegram,
            'city': city,
            'is_featured': 0
        })

        flash("E'loningiz muvaffaqiyatli joylashtirildi va XON_MOTO bozorida e'lon qilindi!", "success")
        return redirect(url_for('vehicle_detail', vehicle_id=new_vehicle_id))

    return render_template('add_listing.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin')
def admin():
    vehicles = database.get_vehicles()
    stats = database.get_stats()
    return render_template('admin.html', vehicles=vehicles, stats=stats)

@app.route('/admin/delete/<int:vehicle_id>', methods=['POST'])
def delete_vehicle_route(vehicle_id):
    database.delete_vehicle(vehicle_id)
    flash("E'lon muvaffaqiyatli o'chirildi.", "info")
    return redirect(url_for('admin'))

@app.route('/api/inquiry', methods=['POST'])
def api_inquiry():
    data = request.get_json() or request.form
    vehicle_id = data.get('vehicle_id')
    name = data.get('name')
    phone = data.get('phone')
    message = data.get('message', '')
    inquiry_type = data.get('inquiry_type', 'xarid')

    if not name or not phone:
        return jsonify({'success': False, 'message': 'Ism va telefon raqami talab qilinadi!'}), 400

    database.add_inquiry(vehicle_id, name, phone, message, inquiry_type)
    return jsonify({
        'success': True,
        'message': "So'rovingiz qabul qilindi! XON_MOTO menejeri tez orada siz bilan bog'lanadi."
    })

@app.route('/api/vehicles')
def api_vehicles():
    category = request.args.get('category')
    search = request.args.get('search')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    sort_by = request.args.get('sort_by')

    vehicles = database.get_vehicles(
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by
    )
    return jsonify(vehicles)

if __name__ == '__main__':
    print("XON_MOTO serveri ishga tushmoqda: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
