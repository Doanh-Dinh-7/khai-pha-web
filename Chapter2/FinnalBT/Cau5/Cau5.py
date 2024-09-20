import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Thiết lập trình duyệt
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Đọc các đường link từ file txt
file_path = "Cau2-5.txt"  # Đường dẫn tới file .txt chứa các đường link
with open(file_path, 'r') as file:
    urls = file.readlines()

# Tạo thư mục để lưu các file txt (nếu chưa có)
output_dir = "saved_txt_content"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Duyệt qua từng URL và lưu nội dung văn bản
for url in urls:
    url = url.strip()  # Loại bỏ ký tự xuống dòng hoặc khoảng trắng thừa
    if not url:
        continue

    # Truy cập trang
    driver.get(url)

    try:
        # Lấy nội dung văn bản từ thẻ div có id="content"
        content_element = driver.find_element(By.ID, "content")
        content_text = content_element.text
    except:
        content_text = "Không tìm thấy nội dung từ thẻ div có id='content'."

    # Tạo tên file từ đường link (loại bỏ các ký tự không hợp lệ)
    file_name = re.sub(r'[^\w\-_\. ]', '_', url) + '.txt'

    # Đường dẫn để lưu file trong thư mục đã tạo
    file_path = os.path.join(output_dir, file_name)

    # Lưu nội dung vào file .txt
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content_text)

    print(f"Đã lưu nội dung của {url} vào file {file_path}")

# Đóng trình duyệt
driver.quit()
