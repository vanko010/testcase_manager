from flask import Flask, render_template, redirect, url_for, session
from flask_migrate import Migrate
from models.testcase_set import db, TestCaseSet
from models.testcase import TestCase
from models.user import User
from routes.testcase_set import testcase_set_bp
from routes.testcase import testcase_bp
from routes.auth import auth_bp, login_required
import os
import sqlite3
from config import Config

# In phiên bản SQLite để debug
print(f"SQLite version: {sqlite3.sqlite_version}")

app = Flask(__name__)
app.config.from_object(Config)

# Đảm bảo thư mục uploads tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Kiểm tra tệp cơ sở dữ liệu
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
print(f"Database URI in app: {db_uri}")

# Trích xuất đường dẫn tệp từ URI
if db_uri.startswith('sqlite:'):
    if db_uri.startswith('sqlite:////'):  # Linux/Unix absolute path
        db_path = db_uri[10:]
    elif db_uri.startswith('sqlite:///'):  # Windows absolute path or relative path
        db_path = db_uri[9:]

    print(f"Extracted database path: {db_path}")
    print(f"Database file exists: {os.path.exists(db_path)}")
    print(f"Database directory exists: {os.path.exists(os.path.dirname(db_path))}")
    print(f"Write permission to directory: {os.access(os.path.dirname(db_path), os.W_OK)}")

    # Thử tạo kết nối trực tiếp với SQLite
    try:
        conn = sqlite3.connect(db_path)
        print("Successfully connected to SQLite database directly")
        conn.close()
    except Exception as e:
        print(f"Error connecting to SQLite directly: {e}")

# Khởi tạo cơ sở dữ liệu
db.init_app(app)
migrate = Migrate(app, db)

# Đăng ký blueprints
app.register_blueprint(testcase_set_bp)
app.register_blueprint(testcase_bp)
app.register_blueprint(auth_bp)


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    if is_admin:
        # Admin có thể xem tất cả
        testcase_sets = TestCaseSet.query.all()
    else:
        # User thường chỉ xem của mình và các testcase công khai
        testcase_sets = TestCaseSet.query.filter(
            (TestCaseSet.user_id == user_id) | (TestCaseSet.is_public == True)
        ).all()

    return render_template('dashboard.html', testcase_sets=testcase_sets)


@app.template_filter('nl2br')
def nl2br(value):
    if value:
        return value.replace('\n', '<br>')
    return ''


# Xử lý lỗi 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Trang không tồn tại"), 404


# Xử lý lỗi 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error="Lỗi hệ thống"), 500


# Thêm biến session vào context của template
@app.context_processor
def inject_session():
    from flask import session
    return dict(session=session)


if __name__ == '__main__':
    with app.app_context():
        print(f"Current working directory: {os.getcwd()}")

        try:
            # Tạo tất cả bảng nếu chưa tồn tại
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {e}")
            import traceback

            traceback.print_exc()

            # Thử giải pháp thay thế: sử dụng cơ sở dữ liệu trong bộ nhớ
            print("\nTrying in-memory database as fallback...")
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            db.init_app(app)
            try:
                db.create_all()
                print("Successfully created tables in memory database!")
                print("WARNING: Data will be lost when application stops.")
            except Exception as e2:
                print(f"Error creating in-memory database: {e2}")

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
