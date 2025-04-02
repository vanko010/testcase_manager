from models.testcase import TestCase
from models.testcase_set import db


def import_json(testcase_set, json_data):
    """
    Nhập các testcase từ dữ liệu JSON vào bộ testcase.

    Args:
        testcase_set (TestCaseSet): Bộ testcase nhập vào
        json_data (list hoặc dict): Dữ liệu JSON chứa các testcase
    """
    if isinstance(json_data, dict):
        # Trường hợp một testcase
        json_data = [json_data]

    # Lấy số thứ tự tiếp theo
    last_testcase = TestCase.query.filter_by(test_case_set_id=testcase_set.id).order_by(TestCase.number.desc()).first()
    next_number = 1 if not last_testcase else last_testcase.number + 1

    for idx, item in enumerate(json_data):
        testcase = TestCase(
            test_case_set_id=testcase_set.id,
            number=next_number + idx,
            description=item.get('Description', ''),
            step=item.get('Step', ''),
            expected_result=item.get('Expected Result', ''),
            status=item.get('Status', 'Not Executed')
        )
        db.session.add(testcase)

    db.session.commit()
