from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash
from models.user import User, db
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# Decorator kiểm tra đăng nhập
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# Decorator kiểm tra quyền admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Bạn không có quyền truy cập trang này', 'danger')
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Tên đăng nhập hoặc email đã tồn tại', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        # Nếu là user đầu tiên, đặt làm admin
        if User.query.count() == 0:
            new_user.is_admin = True

        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Bạn đã đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('auth/profile.html', user=user)


@auth_bp.route('/users')
@admin_required
def user_list():
    users = User.query.all()
    return render_template('auth/user_list.html', users=users)


@auth_bp.route('/users/<int:id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(id):
    user = User.query.get_or_404(id)

    # Không cho phép admin tự hạ cấp mình
    if user.id == session['user_id']:
        flash('Bạn không thể thay đổi quyền của chính mình', 'danger')
        return redirect(url_for('auth.user_list'))

    user.is_admin = not user.is_admin
    db.session.commit()

    action = "cấp" if user.is_admin else "thu hồi"
    flash(f'Đã {action} quyền quản trị cho người dùng {user.username}', 'success')
    return redirect(url_for('auth.user_list'))
