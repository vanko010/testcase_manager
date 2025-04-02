import os
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Đường dẫn tuyệt đối đến thư mục hiện tại
basedir = os.path.abspath(os.path.dirname(__file__))
print(f"Current directory: {basedir}")
print(f"OS name: {os.name}")
print(f"SQLite version: {sqlite3.sqlite_version}")

# Tạo các đường dẫn khác nhau để thử
db_path_1 = os.path.join(basedir, "testcase_manager.db")  # Trong thư mục gốc
db_path_2 = os.path.join(basedir, "instance", "testcase_manager.db")  # Trong thư mục instance
db_path_3 = "/tmp/testcase_manager.db"  # Trong thư mục tmp

# Đảm bảo thư mục instance tồn tại
instance_dir = os.path.join(basedir, "instance")
os.makedirs(instance_dir, exist_ok=True)

# Kiểm tra quyền truy cập
print(f"\n--- Path access check ---")
print(f"Path 1 (root): {db_path_1}")
print(f"  Directory exists: {os.path.exists(os.path.dirname(db_path_1))}")
print(f"  Write permission: {os.access(os.path.dirname(db_path_1), os.W_OK)}")

print(f"Path 2 (instance): {db_path_2}")
print(f"  Directory exists: {os.path.exists(os.path.dirname(db_path_2))}")
print(f"  Write permission: {os.access(os.path.dirname(db_path_2), os.W_OK)}")

print(f"Path 3 (tmp): {db_path_3}")
print(f"  Directory exists: {os.path.exists(os.path.dirname(db_path_3))}")
print(f"  Write permission: {os.access(os.path.dirname(db_path_3), os.W_OK)}")

# Thử kết nối trực tiếp với SQLite
print("\n--- Direct SQLite connection tests ---")
for path, name in [(db_path_1, "root"), (db_path_2, "instance"), (db_path_3, "tmp")]:
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO test (name) VALUES (?)", (f"Test {name}",))
        conn.commit()
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchall()
        conn.close()
        print(f"SQLite direct connection to {name}: SUCCESS")
        print(f"  Query result: {result}")
    except Exception as e:
        print(f"SQLite direct connection to {name}: FAILED")
        print(f"  Error: {e}")

# Thử với Flask-SQLAlchemy
print("\n--- Flask-SQLAlchemy connection tests ---")

# Thử với đường dẫn tuyệt đối 3 dấu /
try:
    app1 = Flask("test_app_1")
    app1.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path_2}"
    app1.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db1 = SQLAlchemy(app1)


    class TestModel(db1.Model):
        id = db1.Column(db1.Integer, primary_key=True)
        name = db1.Column(db1.String(50))


    with app1.app_context():
        db1.create_all()
        test_item = TestModel(name="Test Flask 3 Slashes")
        db1.session.add(test_item)
        db1.session.commit()
        result = TestModel.query.all()
        print(f"Flask-SQLAlchemy connection with 3 slashes: SUCCESS")
        print(f"  Items in database: {len(result)}")
except Exception as e:
    print(f"Flask-SQLAlchemy connection with 3 slashes: FAILED")
    print(f"  Error: {e}")

# Thử với đường dẫn tuyệt đối 4 dấu / (cho Linux)
try:
    app2 = Flask("test_app_2")
    # Đặc biệt cho Linux, sử dụng 4 dấu /
    if os.name == 'posix':  # Linux/Unix/Mac
        db_uri = f"sqlite:////{db_path_2}"
    else:  # Windows
        db_uri = f"sqlite:///{db_path_2}"

    print(f"Testing URI with 4 slashes: {db_uri}")
    app2.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app2.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db2 = SQLAlchemy(app2)


    class TestModel2(db2.Model):
        id = db2.Column(db2.Integer, primary_key=True)
        name = db2.Column(db2.String(50))


    with app2.app_context():
        db2.create_all()
        test_item = TestModel2(name="Test Flask 4 Slashes")
        db2.session.add(test_item)
        db2.session.commit()
        result = TestModel2.query.all()
        print(f"Flask-SQLAlchemy connection with 4 slashes: SUCCESS")
        print(f"  Items in database: {len(result)}")
except Exception as e:
    print(f"Flask-SQLAlchemy connection with 4 slashes: FAILED")
    print(f"  Error: {e}")

# Thử với thư mục /tmp
try:
    app3 = Flask("test_app_3")
    if os.name == 'posix':  # Linux/Unix/Mac
        db_uri = f"sqlite:////{db_path_3}"
    else:  # Windows
        db_uri = f"sqlite:///{db_path_3}"

    app3.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app3.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db3 = SQLAlchemy(app3)


    class TestModel3(db3.Model):
        id = db3.Column(db3.Integer, primary_key=True)
        name = db3.Column(db3.String(50))


    with app3.app_context():
        db3.create_all()
        test_item = TestModel3(name="Test Flask Tmp")
        db3.session.add(test_item)
        db3.session.commit()
        result = TestModel3.query.all()
        print(f"Flask-SQLAlchemy connection to tmp: SUCCESS")
        print(f"  Items in database: {len(result)}")
except Exception as e:
    print(f"Flask-SQLAlchemy connection to tmp: FAILED")
    print(f"  Error: {e}")

# Thử với bộ nhớ
try:
    app4 = Flask("test_app_4")
    app4.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app4.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db4 = SQLAlchemy(app4)


    class TestModel4(db4.Model):
        id = db4.Column(db4.Integer, primary_key=True)
        name = db4.Column(db4.String(50))


    with app4.app_context():
        db4.create_all()
        test_item = TestModel4(name="Test Flask Memory")
        db4.session.add(test_item)
        db4.session.commit()
        result = TestModel4.query.all()
        print(f"Flask-SQLAlchemy connection to memory: SUCCESS")
        print(f"  Items in database: {len(result)}")
except Exception as e:
    print(f"Flask-SQLAlchemy connection to memory: FAILED")
    print(f"  Error: {e}")

# Thử với tham số URI bổ sung
try:
    app5 = Flask("test_app_5")
    if os.name == 'posix':  # Linux/Unix/Mac
        db_uri = f"sqlite:////{db_path_2}?mode=rwc&cache=shared&uri=true"
    else:  # Windows
        db_uri = f"sqlite:///{db_path_2}?mode=rwc&cache=shared&uri=true"

    print(f"Testing URI with parameters: {db_uri}")
    app5.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app5.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db5 = SQLAlchemy(app5)


    class TestModel5(db5.Model):
        id = db5.Column(db5.Integer, primary_key=True)
        name = db5.Column(db5.String(50))


    with app5.app_context():
        db5.create_all()
        test_item = TestModel5(name="Test Flask URI Params")
        db5.session.add(test_item)
        db5.session.commit()
        result = TestModel5.query.all()
        print(f"Flask-SQLAlchemy connection with URI parameters: SUCCESS")
        print(f"  Items in database: {len(result)}")
except Exception as e:
    print(f"Flask-SQLAlchemy connection with URI parameters: FAILED")
    print(f"  Error: {e}")
