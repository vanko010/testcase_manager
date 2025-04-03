/**
 * Chức năng sao chép bảng Danh sách testcase
 * Sử dụng nhiều phương pháp để đảm bảo tính tương thích với các trình duyệt
 */
document.addEventListener('DOMContentLoaded', function() {
    // Lấy nút copy table
    const copyBtn = document.getElementById('copyTableBtn');
    if (!copyBtn) return;

    // Khởi tạo toast nếu nó tồn tại
    const toastEl = document.getElementById('copyToast');
    let toast;
    if (toastEl && typeof bootstrap !== 'undefined') {
        toast = new bootstrap.Toast(toastEl);
    }

    // Đăng ký sự kiện click cho nút Copy Table
    copyBtn.addEventListener('click', function() {
        // Lấy bảng Danh sách testcase
        const table = document.getElementById('testcaseTable');
        if (!table) {
            alert('Không tìm thấy bảng Danh sách testcase!');
            return;
        }

        // Chuẩn bị nội dung bảng để sao chép
        let tableText = extractTableContent(table);
        copyTextToClipboard(tableText);
    });

    /**
     * Trích xuất nội dung bảng thành văn bản có định dạng
     * @param {HTMLTableElement} table - Bảng cần trích xuất nội dung
     * @returns {string} Nội dung bảng dạng văn bản
     */
    function extractTableContent(table) {
        let result = '';

        // Lấy tất cả hàng trong bảng (bao gồm cả header)
        const rows = table.querySelectorAll('tr');

        // Duyệt qua từng hàng
        rows.forEach(row => {
            let rowData = [];

            // Lấy tất cả ô trong hàng (th hoặc td)
            const cells = row.querySelectorAll('th, td');

            // Duyệt qua từng ô
            cells.forEach((cell, index) => {
                // Bỏ qua cột thao tác (cột cuối nếu chứa nút)
                if (cell.querySelector('.btn-group')) {
                    return;
                }

                // Lấy nội dung text, loại bỏ khoảng trắng thừa
                let cellText = cell.textContent.trim();

                // Nếu ô chứa badge (như trạng thái), chỉ lấy text của badge
                if (cell.querySelector('.badge')) {
                    cellText = cell.querySelector('.badge').textContent.trim();
                }

                // Thêm nội dung ô vào mảng dữ liệu hàng
                rowData.push(cellText);
            });

            // Nếu có dữ liệu trong hàng, thêm vào kết quả
            if (rowData.length > 0) {
                result += rowData.join('\t') + '\n';
            }
        });

        return result;
    }

    /**
     * Sao chép văn bản vào clipboard
     * @param {string} text - Văn bản cần sao chép
     */
    function copyTextToClipboard(text) {
        console.log("Nội dung sao chép:", text);

        // Phương pháp 1: Clipboard API (hiện đại)
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text)
                .then(() => {
                    console.log("Sao chép thành công bằng Clipboard API");
                    showSuccessMessage();
                })
                .catch(err => {
                    console.error("Lỗi Clipboard API:", err);
                    fallbackCopyMethod(text);
                });
        }
        // Phương pháp 2: execCommand (cũ hơn, hỗ trợ nhiều trình duyệt)
        else {
            fallbackCopyMethod(text);
        }
    }

    /**
     * Phương pháp sao chép thay thế sử dụng document.execCommand
     * @param {string} text - Văn bản cần sao chép
     */
    function fallbackCopyMethod(text) {
        // Tạo phần tử textarea tạm thời
        const textArea = document.createElement("textarea");
        textArea.value = text;

        // Cấu hình để ẩn phần tử nhưng vẫn có thể select
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);

        // Focus, select và thực hiện lệnh copy
        textArea.focus();
        textArea.select();

        let success = false;
        try {
            success = document.execCommand('copy');
        } catch (err) {
            console.error("Lỗi execCommand:", err);
        }

        // Xóa phần tử tạm
        document.body.removeChild(textArea);

        // Hiển thị thông báo dựa trên kết quả
        if (success) {
            console.log("Sao chép thành công bằng execCommand");
            showSuccessMessage();
        } else {
            console.error("Không thể sao chép văn bản");
            alert("Không thể sao chép bảng. Vui lòng thử lại hoặc sử dụng Ctrl+C.");
        }
    }

    /**
     * Hiển thị thông báo sao chép thành công
     */
    function showSuccessMessage() {
        if (toast) {
            toast.show();
        } else {
            alert('Đã sao chép bảng Danh sách testcase vào clipboard!');
        }
    }
});
