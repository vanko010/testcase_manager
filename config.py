import os
import secrets


class Config:
    # Tạo SECRET_KEY ngẫu nhiên nếu không có
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cấu hình đường dẫn cơ bản
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Đường dẫn đến thư mục upload
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Tạo thư mục instance nếu chưa tồn tại
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Đường dẫn tuyệt đối đến tệp database
    db_path = os.path.join(instance_path, 'testcase_manager.db')

    # Cú pháp đúng cho đường dẫn tuyệt đối trên Linux/Unix (4 dấu /)
    if os.name == 'posix':  # Linux/Unix/Mac
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}?timeout=10"
    else:  # Windows
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}?timeout=10"

    # In thông tin debug
    print(f"OS name: {os.name}")
    print(f"Database file path: {db_path}")
    print(f"Database URI: {SQLALCHEMY_DATABASE_URI}")

    # Cấu hình cho PostgreSQL (production)
    DB_USERNAME = os.environ.get('DB_USERNAME', '')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'testcase_manager')
