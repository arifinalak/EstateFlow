from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import errorcode
from pathlib import Path
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "realestate_secret_key")
SCHEMA_READY = False

DB_NAME = os.environ.get("DB_NAME", "realestate")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "port": int(os.environ.get("DB_PORT", "3306")),
}

PROPERTY_TYPE_OPTIONS = [
    "land",
    "office",
    "bungalow",
    "apartment",
    "villa",
    "studio",
]

DEFAULT_TYPE_IMAGES = {
    "land": "gulshan-land.jpg",
    "office": "corporate-house.jpeg",
    "bungalow": "banglow.jpg",
    "apartment": "cozy-studio-apartment.jpg",
    "villa": "pride-villa.jpg",
    "studio": "cozy-studio-apartment.jpg",
}

IMAGE_OPTIONS = [
    "banglow.jpg",
    "corporate-house.jpeg",
    "cozy-studio-apartment.jpg",
    "gulshan-land.jpg",
    "lakeview-house.jpg",
    "pride-villa.jpg",
]


def ensure_runtime_tables(db):
    cur = db.cursor()
    try:
        try:
            cur.execute("ALTER TABLE properties ADD COLUMN property_type VARCHAR(30) DEFAULT 'apartment'")
        except mysql.connector.Error as err:
            if err.errno != errorcode.ER_DUP_FIELDNAME:
                raise

        try:
            cur.execute("ALTER TABLE properties ADD COLUMN image_path VARCHAR(255)")
        except mysql.connector.Error as err:
            if err.errno != errorcode.ER_DUP_FIELDNAME:
                raise

        cur.execute("UPDATE properties SET property_type='apartment' WHERE property_type IS NULL OR property_type='' ")
        cur.execute(
            """
            UPDATE properties
            SET image_path = CASE property_type
                WHEN 'land' THEN 'gulshan-land.jpg'
                WHEN 'office' THEN 'corporate-house.jpeg'
                WHEN 'bungalow' THEN 'banglow.jpg'
                WHEN 'villa' THEN 'pride-villa.jpg'
                WHEN 'studio' THEN 'cozy-studio-apartment.jpg'
                ELSE 'lakeview-house.jpg'
            END
            WHERE image_path IS NULL OR image_path=''
            """
        )

        # Convert default demo names and property names to romanized Bengali style.
        cur.execute("UPDATE users SET name='Md. Rashed Chowdhury' WHERE email='admin@demo.com'")
        cur.execute("UPDATE users SET name='Arifa Rahman' WHERE email='agent@demo.com'")
        cur.execute("UPDATE users SET name='Sumaiya Islam' WHERE email='buyer@demo.com'")
        cur.execute("UPDATE users SET name='Tanvir Hasan' WHERE email='investor@demo.com'")

        cur.execute(
            """
            UPDATE properties
            SET title='Dhanmondi Shanti Apartment', property_type='apartment', image_path='lakeview-house.jpg'
            WHERE title IN ('Modern Downtown Apartment', 'ধানমন্ডি শান্তি অ্যাপার্টমেন্ট')
            """
        )
        cur.execute(
            """
            UPDATE properties
            SET title='Uttara Paribarik Villa', property_type='villa', image_path='pride-villa.jpg'
            WHERE title IN ('Spacious Family Villa', 'উত্তরা পারিবারিক ভিলা')
            """
        )
        cur.execute(
            """
            UPDATE properties
            SET title='Mirpur Cozy Studio', property_type='studio', image_path='cozy-studio-apartment.jpg'
            WHERE title IN ('Cozy Studio Flat', 'মিরপুর কোজি স্টুডিও')
            """
        )
        cur.execute(
            """
            UPDATE properties
            SET title='Gulshan Lakeview Banglow', property_type='bungalow', image_path='banglow.jpg'
            WHERE title IN ('Luxury Penthouse', 'গুলশান লেকভিউ বাংলো', 'লেকভিউ বাংলো')
            """
        )
        cur.execute(
            """
            UPDATE properties
            SET title='Motijheel Corporate Office', property_type='office', image_path='corporate-house.jpeg'
            WHERE title IN ('Commercial Office Space', 'মতিঝিল কর্পোরেট অফিস', 'গুলশান কর্পোরেট অফিস স্পেস')
            """
        )
        cur.execute(
            """
            UPDATE properties
            SET title='Gulshan Prime Land', property_type='land', image_path='gulshan-land.jpg'
            WHERE title IN ('Beachside Bungalow', 'গুলশান প্রাইম ল্যান্ড')
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS inquiries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                property_id INT NOT NULL,
                buyer_id INT NOT NULL,
                agent_id INT NOT NULL,
                message TEXT NOT NULL,
                agent_message TEXT,
                status ENUM('new','in_progress','completed','replied','closed') DEFAULT 'new',
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
                FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # Backward-compatible migration for existing inquiry tables.
        try:
            cur.execute("ALTER TABLE inquiries ADD COLUMN agent_message TEXT")
        except mysql.connector.Error as err:
            if err.errno != errorcode.ER_DUP_FIELDNAME:
                raise

        cur.execute(
            """
            ALTER TABLE inquiries
            MODIFY status ENUM('new','in_progress','completed','replied','closed') DEFAULT 'new'
            """
        )
        db.commit()
    finally:
        cur.close()


def init_database_from_schema():
    schema_path = Path(__file__).with_name("schema.sql")
    if not schema_path.exists():
        raise FileNotFoundError("schema.sql not found beside app.py")

    with schema_path.open("r", encoding="utf-8") as f:
        sql = f.read()

    # Remove single-line SQL comments so statements split correctly.
    cleaned_lines = []
    for line in sql.splitlines():
        if line.strip().startswith("--"):
            continue
        cleaned_lines.append(line)
    sql = "\n".join(cleaned_lines)

    db = mysql.connector.connect(**DB_CONFIG)
    cur = db.cursor()
    try:
        for statement in sql.split(";"):
            stmt = statement.strip()
            if not stmt:
                continue
            cur.execute(stmt)
        db.commit()
    finally:
        cur.close()
        db.close()

# ─── DB CONNECTION ────────────────────────────────────────────────────────────
def get_db():
    global SCHEMA_READY
    try:
        db = mysql.connector.connect(database=DB_NAME, **DB_CONFIG)
        if not SCHEMA_READY:
            ensure_runtime_tables(db)
            SCHEMA_READY = True
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            init_database_from_schema()
            db = mysql.connector.connect(database=DB_NAME, **DB_CONFIG)
            ensure_runtime_tables(db)
            SCHEMA_READY = True
            return db
        raise

# ─── DECORATORS ───────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ─── AUTH ─────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM properties WHERE status='available' LIMIT 6")
    props = cur.fetchall(); db.close()
    return render_template('index.html', properties=props, property_types=PROPERTY_TYPE_OPTIONS)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        db = get_db(); cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                    (request.form['email'], request.form['password']))
        user = cur.fetchone(); db.close()
        if user:
            session['user_id'] = user['id']
            session['name']    = user['name']
            session['role']    = user['role']
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        db = get_db(); cur = db.cursor()
        try:
            cur.execute("INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,%s)",
                (request.form['name'], request.form['email'],
                 request.form['password'], request.form['role']))
            db.commit(); flash('Registered! Please login.', 'success')
            return redirect(url_for('login'))
        except: flash('Email already exists.', 'danger')
        finally: db.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    role = session['role']
    if role == 'admin':    return redirect(url_for('admin_dashboard'))
    if role == 'agent':    return redirect(url_for('agent_dashboard'))
    if role == 'investor': return redirect(url_for('investor_dashboard'))
    return redirect(url_for('buyer_dashboard'))

# ─── PROPERTIES ───────────────────────────────────────────────────────────────
@app.route('/properties')
def properties():
    db = get_db(); cur = db.cursor(dictionary=True)
    q = request.args.get('q',''); city = request.args.get('city','')
    property_type = request.args.get('property_type', '')
    sql = "SELECT * FROM properties WHERE 1=1"; params = []
    if q:    sql += " AND title LIKE %s";  params.append(f'%{q}%')
    if city: sql += " AND city LIKE %s";   params.append(f'%{city}%')
    if property_type: sql += " AND property_type=%s"; params.append(property_type)
    cur.execute(sql, params); props = cur.fetchall(); db.close()
    return render_template(
        'properties.html',
        properties=props,
        q=q,
        city=city,
        property_type=property_type,
        property_types=PROPERTY_TYPE_OPTIONS,
    )

@app.route('/property/<int:pid>')
def property_detail(pid):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT p.*, u.name AS agent_name FROM properties p LEFT JOIN users u ON p.agent_id=u.id WHERE p.id=%s", (pid,))
    prop = cur.fetchone(); db.close()
    return render_template('property_detail.html', prop=prop)

@app.route('/save_property/<int:pid>')
@login_required
def save_property(pid):
    if session.get('role') != 'buyer':
        flash('Only buyers can save listings.', 'warning')
        return redirect(request.referrer or url_for('property_detail', pid=pid))

    db = get_db(); cur = db.cursor()
    try:
        cur.execute("INSERT INTO saved_listings (user_id,property_id) VALUES (%s,%s)", (session['user_id'], pid))
        db.commit(); flash('Property saved!', 'success')
    except: flash('Already saved.', 'info')
    finally: db.close()
    return redirect(request.referrer or url_for('property_detail', pid=pid))


@app.route('/inquire/<int:pid>', methods=['POST'])
@login_required
@role_required('buyer')
def inquire_property(pid):
    message = request.form.get('message', '').strip()
    if not message:
        flash('Please write a message before sending inquiry.', 'warning')
        return redirect(url_for('property_detail', pid=pid))

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id, title, agent_id FROM properties WHERE id=%s", (pid,))
    prop = cur.fetchone()

    if not prop:
        db.close()
        flash('Property not found.', 'danger')
        return redirect(url_for('properties'))

    if not prop['agent_id']:
        db.close()
        flash('This property has no assigned agent yet.', 'warning')
        return redirect(url_for('property_detail', pid=pid))

    cur2 = db.cursor()
    cur2.execute(
        "INSERT INTO inquiries (property_id,buyer_id,agent_id,message) VALUES (%s,%s,%s,%s)",
        (pid, session['user_id'], prop['agent_id'], message),
    )
    db.commit()
    db.close()

    flash('Inquiry sent to agent successfully.', 'success')
    return redirect(url_for('property_detail', pid=pid))

# ─── BUYER ────────────────────────────────────────────────────────────────────
@app.route('/buyer')
@login_required
@role_required('buyer')
def buyer_dashboard():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT p.* FROM saved_listings s JOIN properties p ON s.property_id=p.id WHERE s.user_id=%s", (session['user_id'],))
    saved = cur.fetchall()
    cur.execute(
        """
        SELECT i.*, p.title AS property_title, u.name AS agent_name
        FROM inquiries i
        JOIN properties p ON i.property_id = p.id
        JOIN users u ON i.agent_id = u.id
        WHERE i.buyer_id=%s
        ORDER BY i.created DESC
        """,
        (session['user_id'],),
    )
    inquiries = cur.fetchall()
    db.close()
    return render_template('buyer_dashboard.html', saved=saved, inquiries=inquiries)

# ─── AGENT ────────────────────────────────────────────────────────────────────
@app.route('/agent')
@login_required
@role_required('agent')
def agent_dashboard():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM properties WHERE agent_id=%s", (session['user_id'],))
    listings = cur.fetchall()
    cur.execute("SELECT * FROM leads WHERE agent_id=%s", (session['user_id'],))
    leads = cur.fetchall()
    cur.execute(
        """
        SELECT i.*, p.title AS property_title, u.name AS buyer_name, u.email AS buyer_email
        FROM inquiries i
        JOIN properties p ON i.property_id = p.id
        JOIN users u ON i.buyer_id = u.id
        WHERE i.agent_id=%s
        ORDER BY i.created DESC
        """,
        (session['user_id'],),
    )
    inquiries = cur.fetchall()
    db.close()
    return render_template(
        'agent_dashboard.html',
        listings=listings,
        leads=leads,
        inquiries=inquiries,
    )


@app.route('/update_inquiry/<int:iid>', methods=['POST'])
@login_required
@role_required('agent')
def update_inquiry(iid):
    action = request.form.get('action', '').strip()
    agent_message = request.form.get('agent_message', '').strip()

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT id, status FROM inquiries WHERE id=%s AND agent_id=%s",
        (iid, session['user_id']),
    )
    inquiry = cur.fetchone()

    if not inquiry:
        db.close()
        flash('Inquiry not found or access denied.', 'danger')
        return redirect(url_for('agent_dashboard'))

    if action == 'in_progress':
        new_status = 'in_progress'
    elif action == 'completed':
        new_status = 'completed'
    elif action == 'send_message':
        new_status = inquiry['status']
    else:
        db.close()
        flash('Invalid inquiry action.', 'warning')
        return redirect(url_for('agent_dashboard'))

    cur2 = db.cursor()
    cur2.execute(
        "UPDATE inquiries SET status=%s, agent_message=%s WHERE id=%s AND agent_id=%s",
        (new_status, agent_message if agent_message else None, iid, session['user_id']),
    )
    db.commit()
    db.close()

    flash('Inquiry updated.', 'success')
    return redirect(url_for('agent_dashboard'))

@app.route('/add_property', methods=['GET','POST'])
@login_required
@role_required('agent','admin')
def add_property():
    if request.method == 'POST':
        property_type = request.form.get('property_type', 'apartment')
        image_path = request.form.get('image_path', '').strip() or DEFAULT_TYPE_IMAGES.get(property_type, 'lakeview-house.jpg')
        db = get_db(); cur = db.cursor()
        cur.execute("INSERT INTO properties (title,description,price,city,bedrooms,bathrooms,area,property_type,image_path,status,agent_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (request.form['title'], request.form['description'], request.form['price'],
             request.form['city'],  request.form['bedrooms'],   request.form['bathrooms'],
             request.form['area'],  property_type, image_path, request.form['status'], session['user_id']))
        db.commit(); db.close()
        flash('Property added!', 'success')
        return redirect(url_for('agent_dashboard'))
    return render_template(
        'add_property.html',
        property_types=PROPERTY_TYPE_OPTIONS,
        image_options=IMAGE_OPTIONS,
    )

# ─── ADMIN ────────────────────────────────────────────────────────────────────
@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users");      users = cur.fetchall()
    cur.execute("SELECT * FROM properties"); props = cur.fetchall()
    cur.execute("SELECT COUNT(*) AS c FROM properties"); t_props = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM users");      t_users = cur.fetchone()['c']
    cur.execute("SELECT COUNT(*) AS c FROM leads");      t_leads = cur.fetchone()['c']
    db.close()
    return render_template('admin_dashboard.html', users=users, properties=props,
                           t_props=t_props, t_users=t_users, t_leads=t_leads)

# ─── INVESTOR ─────────────────────────────────────────────────────────────────
@app.route('/investor')
@login_required
@role_required('investor')
def investor_dashboard():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM portfolio WHERE investor_id=%s", (session['user_id'],))
    portfolio = cur.fetchall(); db.close()
    return render_template('investor_dashboard.html', portfolio=portfolio)

@app.route('/calculator', methods=['GET','POST'])
@login_required
@role_required('investor')
def calculator():
    result = None
    if request.method == 'POST':
        price  = float(request.form['price'])
        rent   = float(request.form['monthly_rent'])
        exp    = float(request.form['monthly_expenses'])
        down   = float(request.form['down_payment']) / 100
        noi    = (rent - exp) * 12
        cap    = (noi / price) * 100
        cash_r = (noi / (price * down)) * 100 if down else 0
        result = {'noi': round(noi,2), 'cap_rate': round(cap,2), 'cash_return': round(cash_r,2)}
    return render_template('calculator.html', result=result)

@app.route('/add_portfolio', methods=['POST'])
@login_required
@role_required('investor')
def add_portfolio():
    db = get_db(); cur = db.cursor()
    cur.execute("INSERT INTO portfolio (investor_id,property_name,purchase_price,current_value,monthly_income) VALUES (%s,%s,%s,%s,%s)",
        (session['user_id'], request.form['property_name'], request.form['purchase_price'],
         request.form['current_value'], request.form['monthly_income']))
    db.commit(); db.close()
    flash('Added to portfolio!', 'success')
    return redirect(url_for('investor_dashboard'))

# ─── CRM LEADS ────────────────────────────────────────────────────────────────
@app.route('/leads')
@login_required
@role_required('agent','admin')
def leads():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM leads WHERE agent_id=%s", (session['user_id'],))
    leads = cur.fetchall(); db.close()
    return render_template('leads.html', leads=leads)

@app.route('/add_lead', methods=['POST'])
@login_required
@role_required('agent','admin')
def add_lead():
    db = get_db(); cur = db.cursor()
    cur.execute("INSERT INTO leads (agent_id,name,email,phone,status,notes) VALUES (%s,%s,%s,%s,'new',%s)",
        (session['user_id'], request.form['name'], request.form['email'],
         request.form['phone'], request.form['notes']))
    db.commit(); db.close()
    flash('Lead added!', 'success')
    return redirect(url_for('leads'))

@app.route('/update_lead/<int:lid>', methods=['POST'])
@login_required
def update_lead(lid):
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE leads SET status=%s, notes=%s WHERE id=%s",
                (request.form['status'], request.form['notes'], lid))
    db.commit(); db.close()
    flash('Lead updated!', 'success')
    return redirect(url_for('leads'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
