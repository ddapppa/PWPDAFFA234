# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import create_app, db
from models import User

app = create_app()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Registrasi Pengguna
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(
            username=username,
            role=role,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login Pengguna
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Email atau password salah.')

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    users = User.query.all()
    return render_template('dashboard.html', users=users)

# Tambah Pengguna
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(
            username=username,
            role=role,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('add_user.html')

# Edit Pengguna
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_to_edit = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user_to_edit.username = request.form.get('username')
        user_to_edit.role = request.form.get('role')
        user_to_edit.email = request.form.get('email')

        new_password = request.form.get('password')
        if new_password:
            user_to_edit.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_user.html', user=user_to_edit)

# Hapus Pengguna
@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
