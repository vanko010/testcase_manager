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
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if 'user_id' in session:
        return redirect(url_for('dashboard'))  # Nếu đã đăng nhập, chuyển hướng về Dashboard

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
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if 'user_id' in session:
        return redirect(url_for('dashboard'))  # Nếu đã đăng nhập, chuyển hướng về Dashboard

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
    return redirect(url_for('auth.login'))  # Chuyển hướng về trang đăng nhập


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


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Kiểm tra mật khẩu hiện tại
        if not user.check_password(current_password):
            flash('Mật khẩu hiện tại không đúng', 'danger')
            return redirect(url_for('auth.change_password'))

        # Kiểm tra mật khẩu mới và xác nhận
        if new_password != confirm_password:
            flash('Mật khẩu mới không khớp', 'danger')
            return redirect(url_for('auth.change_password'))

        # Cập nhật mật khẩu mới
        user.set_password(new_password)
        db.session.commit()

        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/change_password.html')


@auth_bp.route('/users/<int:id>/reset-password', methods=['GET', 'POST'])
@admin_required
def reset_user_password(id):
    user = User.query.get_or_404(id)

    # Ngăn chặn admin đổi mật khẩu của chính mình qua route này
    if user.id == session['user_id']:
        flash('Vui lòng sử dụng trang đổi mật khẩu cá nhân', 'warning')
        return redirect(url_for('auth.change_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Kiểm tra mật khẩu mới và xác nhận
        if new_password != confirm_password:
            flash('Mật khẩu mới không khớp', 'danger')
            return redirect(url_for('auth.reset_user_password', id=id))

        # Cập nhật mật khẩu mới
        user.set_password(new_password)
        db.session.commit()

        flash(f'Đặt lại mật khẩu cho người dùng {user.username} thành công!', 'success')
        return redirect(url_for('auth.user_list'))

    return render_template('auth/reset_password.html', user=user)

@auth_bp.route('/create-user', methods=['GET', 'POST'])
def create_user():
    # Kiểm tra quyền admin
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Bạn không có quyền truy cập trang này', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # Lấy vai trò từ form

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Tên đăng nhập hoặc email đã tồn tại', 'danger')
            return redirect(url_for('auth.create_user'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        # Gán vai trò
        if role == 'admin':
            new_user.is_admin = True
        else:
            new_user.is_admin = False

        db.session.add(new_user)
        db.session.commit()

        flash('Tạo tài khoản thành công!', 'success')
        return redirect(url_for('auth.user_list'))

    return render_template('auth/create_user.html')
