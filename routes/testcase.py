from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.testcase_set import db, TestCaseSet
from models.testcase import TestCase
from routes.auth import login_required

testcase_bp = Blueprint('testcase', __name__, url_prefix='/testcase')


@testcase_bp.route('/new/<int:testcase_set_id>', methods=['GET', 'POST'])
@login_required
def create(testcase_set_id):
    testcase_set = TestCaseSet.query.get_or_404(testcase_set_id)

    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    if not is_admin and testcase_set.user_id != user_id:
        flash('Bạn không có quyền thêm testcase vào bộ này', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            last_testcase = TestCase.query.filter_by(test_case_set_id=testcase_set_id).order_by(
                TestCase.number.desc()).first()
            number = 1 if not last_testcase else last_testcase.number + 1

            description = request.form['description']
            step = request.form['step']
            expected_result = request.form['expected_result']
            status = request.form['status']

            testcase = TestCase(
                test_case_set_id=testcase_set_id,
                number=number,
                description=description,
                step=step,
                expected_result=expected_result,
                status=status
            )

            db.session.add(testcase)
            db.session.commit()  # Commit sau khi thêm testcase
            flash('Tạo testcase thành công!', 'success')
            return redirect(url_for('testcase_set.detail', id=testcase_set_id))
        except Exception as e:
            db.session.rollback()  # Rollback nếu có lỗi
            flash('Có lỗi xảy ra khi thêm testcase: ' + str(e), 'danger')

    return render_template('testcase_form.html', testcase_set=testcase_set)



@testcase_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    testcase = TestCase.query.get_or_404(id)
    testcase_set = testcase.test_case_set

    # Kiểm tra quyền
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    if not is_admin and testcase_set.user_id != user_id:
        flash('Bạn không có quyền chỉnh sửa testcase này', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        testcase.description = request.form['description']
        testcase.step = request.form['step']
        testcase.expected_result = request.form['expected_result']
        testcase.status = request.form['status']

        db.session.commit()

        flash('Cập nhật testcase thành công!', 'success')
        return redirect(url_for('testcase_set.detail', id=testcase.test_case_set_id))

    return render_template('testcase_form.html', testcase=testcase, testcase_set=testcase.test_case_set)


@testcase_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    testcase = TestCase.query.get_or_404(id)
    testcase_set = testcase.test_case_set
    testcase_set_id = testcase.test_case_set_id

    # Kiểm tra quyền
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    if not is_admin and testcase_set.user_id != user_id:
        flash('Bạn không có quyền xóa testcase này', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(testcase)
    db.session.commit()

    flash('Xóa testcase thành công!', 'success')
    return redirect(url_for('testcase_set.detail', id=testcase_set_id))
