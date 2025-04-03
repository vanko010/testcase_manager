from models.testcase import TestCase
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models.testcase_set import db, TestCaseSet
from models.user import User
import json
from utils.json_import import import_json
from utils.excel_export import export_to_excel
from routes.auth import login_required, admin_required
from datetime import datetime
from sqlalchemy import desc
testcase_set_bp = Blueprint('testcase_set', __name__, url_prefix='/testcase-set')


@testcase_set_bp.route('/')
@login_required
def index():
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


@testcase_set_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        is_public = 'is_public' in request.form

        testcase_set = TestCaseSet(
            name=name,
            description=description,
            user_id=session['user_id'],
            is_public=is_public
        )

        db.session.add(testcase_set)
        db.session.commit()

        flash('Tạo bộ testcase thành công!', 'success')
        return redirect(url_for('testcase_set.detail', id=testcase_set.id))

    return render_template('testcase_set_form.html')


@testcase_set_bp.route('/<int:id>')
@login_required
def detail(id):
    """Hiển thị chi tiết của một bộ test case"""
    testcase_set = TestCaseSet.query.get_or_404(id)

    # Kiểm tra quyền truy cập
    if not testcase_set.is_public and testcase_set.user_id != session.get('user_id') and not session.get('is_admin'):
        flash('Bạn không có quyền xem bộ test case này', 'danger')
        return redirect(url_for('testcase_set.index'))

    testcases = TestCase.query.filter_by(test_case_set_id=id).all()

    return render_template('testcase_set_detail.html', testcase_set=testcase_set, testcases=testcases)


@testcase_set_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    testcase_set = TestCaseSet.query.get_or_404(id)

    # Kiểm tra quyền
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    if not is_admin and testcase_set.user_id != user_id:
        flash('Bạn không có quyền chỉnh sửa bộ testcase này', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        testcase_set.name = request.form['name']
        testcase_set.description = request.form['description']
        testcase_set.is_public = 'is_public' in request.form

        db.session.commit()

        flash('Cập nhật bộ testcase thành công!', 'success')
        return redirect(url_for('testcase_set.detail', id=testcase_set.id))

    return render_template('testcase_set_form.html', testcase_set=testcase_set)


@testcase_set_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Xóa một bộ test case"""
    testcase_set = TestCaseSet.query.get_or_404(id)

    # Kiểm tra quyền xóa
    if testcase_set.user_id != session.get('user_id') and not session.get('is_admin'):
        flash('Bạn không có quyền xóa bộ test case này', 'danger')
        return redirect(url_for('testcase_set.index'))

    # Xóa tất cả test case liên quan - Đảm bảo sử dụng test_case_set_id
    TestCase.query.filter_by(test_case_set_id=id).delete()

    # Xóa bộ test case
    db.session.delete(testcase_set)
    db.session.commit()

    flash('Xóa bộ test case thành công', 'success')
    return redirect(url_for('testcase_set.index'))



@testcase_set_bp.route('/<int:id>/import', methods=['POST'])
@login_required
def import_testcases(id):
    testcase_set = TestCaseSet.query.get_or_404(id)

    # Kiểm tra quyền
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    if not is_admin and testcase_set.user_id != user_id:
        flash('Bạn không có quyền nhập testcase vào bộ này', 'danger')
        return redirect(url_for('dashboard'))

    if 'file' not in request.files:
        flash('Không tìm thấy file', 'error')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('Chưa chọn file', 'error')
        return redirect(request.url)

    if file and file.filename.endswith('.json'):
        try:
            json_data = json.load(file)
            import_json(testcase_set, json_data)
            flash('Import testcase thành công!', 'success')
        except Exception as e:
            flash(f'Lỗi khi import: {str(e)}', 'error')
    else:
        flash('File không hợp lệ. Vui lòng upload file JSON.', 'error')

    return redirect(url_for('testcase_set.detail', id=testcase_set.id))

@testcase_set_bp.route('/<int:id>/export-excel')
@login_required
def export_excel(id):
    """Xuất bộ testcase ra định dạng Excel"""
    testcase_set = TestCaseSet.query.get_or_404(id)

    # Kiểm tra quyền
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    if not is_admin and testcase_set.user_id != user_id and not testcase_set.is_public:
        flash('Bạn không có quyền xuất bộ testcase này', 'danger')
        return redirect(url_for('testcase_set.index'))

    return export_to_excel(testcase_set)


@testcase_set_bp.route('/<int:id>/export')
@login_required
def export_testcases(id):
    testcase_set = TestCaseSet.query.get_or_404(id)

    # Kiểm tra quyền
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    if not is_admin and testcase_set.user_id != user_id and not testcase_set.is_public:
        flash('Bạn không có quyền xuất bộ testcase này', 'danger')
        return redirect(url_for('dashboard'))

    return export_to_excel(testcase_set)


@testcase_set_bp.route('/<int:id>/toggle-public', methods=['POST'])
@login_required
def toggle_public(id):
    testcase_set = TestCaseSet.query.get_or_404(id)

    # Kiểm tra quyền
    if testcase_set.user_id != session['user_id'] and not session.get('is_admin'):
        flash('Bạn không có quyền chỉnh sửa bộ testcase này', 'danger')
        return redirect(url_for('dashboard'))

    testcase_set.is_public = not testcase_set.is_public
    db.session.commit()

    action = "công khai" if testcase_set.is_public else "riêng tư"
    flash(f'Đã đặt bộ testcase "{testcase_set.name}" thành {action}', 'success')
    return redirect(url_for('testcase_set.detail', id=testcase_set.id))

@testcase_set_bp.route('/export/<int:id>')
@login_required
def export(id):
    """Xuất bộ test case dưới dạng JSON"""
    testcase_set = TestCaseSet.query.get_or_404(id)

    # Kiểm tra quyền truy cập
    if not testcase_set.is_public and testcase_set.user_id != session.get('user_id') and not session.get('is_admin'):
        flash('Bạn không có quyền xuất bộ test case này', 'danger')
        return redirect(url_for('testcase_set.index'))

    # Logic xuất bộ test case
    testcases = TestCase.query.filter_by(test_case_set_id=id).all()  # Lưu ý: sử dụng test_case_set_id

    data = {
        'testcase_set': {
            'id': testcase_set.id,
            'name': testcase_set.name,
            'description': testcase_set.description,
            'created_at': testcase_set.created_at.isoformat() if testcase_set.created_at else None,
            'is_public': testcase_set.is_public
        },
        'testcases': []
    }

    for tc in testcases:
        data['testcases'].append({
            'id': tc.id,
            'description': tc.description,
            'step': tc.step,
            'expected_result': tc.expected_result,
            'status': tc.status,
            'created_at': tc.created_at.isoformat() if tc.created_at else None
        })

    # Tạo response với JSON
    response = jsonify(data)
    response.headers['Content-Disposition'] = f'attachment; filename=testcase_set_{id}.json'
    return response
