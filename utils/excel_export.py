import io
import pandas as pd
from flask import send_file
from datetime import datetime


def export_to_excel(testcase_set):
    """
    Xuất bộ testcase ra định dạng Excel.

    Args:
        testcase_set (TestCaseSet): Bộ testcase cần xuất

    Returns:
        Response: Flask response với file Excel đính kèm
    """
    data = []

    for testcase in testcase_set.test_cases:
        data.append({
            'STT': testcase.number,
            'Test Description': testcase.description,
            'Step': testcase.step,
            'Expected Result': testcase.expected_result,
            'Status': testcase.status
        })

    df = pd.DataFrame(data)

    # Tạo buffer để lưu file Excel
    output = io.BytesIO()

    # Tạo Excel writer
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Test Cases', index=False)

        # Lấy workbook và worksheet từ xlsxwriter
        workbook = writer.book
        worksheet = writer.sheets['Test Cases']

        # Đặt độ rộng cột
        worksheet.set_column('A:A', 5)  # STT
        worksheet.set_column('B:B', 30)  # Description
        worksheet.set_column('C:C', 40)  # Step
        worksheet.set_column('D:D', 40)  # Expected Result
        worksheet.set_column('E:E', 15)  # Status

    # Di chuyển về đầu stream
    output.seek(0)

    # Tạo tên file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{testcase_set.name.replace(' ', '_')}_{timestamp}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
