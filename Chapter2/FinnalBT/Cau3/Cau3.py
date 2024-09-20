from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# Thiết lập trình duyệt
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Số trang cần cào
num_pages = 5  # Thay đổi theo số lượng trang bạn muốn

# Danh sách để lưu thông tin bài báo
articles = []

for page in range(1, num_pages + 1):
    url = f"https://baodaklak.vn/khoa-hoc-cong-nghe/?paged={page}"
    driver.get(url)
    # Cào các thẻ a với class 'title1' hoặc 'title1 photo'
    elements = driver.find_elements(By.CSS_SELECTOR, "div.item.row15")

    for element in elements:
        # Lấy tiêu đề
        title_element = element.find_element(By.CSS_SELECTOR, "a.title1, a.title1.photo")
        title = title_element.text
        if(title == ""):
            continue
        href = title_element.get_attribute('href')

        # Lấy tóm tắt
        try:
            description_element = element.find_element(By.CSS_SELECTOR, "div.des")
            description = description_element.text
            if(description == ""):
                continue
        except NoSuchElementException:
            description = "Không có tóm tắt"

        # Lấy ngày đăng
        try:
            date_element = element.find_element(By.CSS_SELECTOR, "div.date.row10")
            date = date_element.text
            if(date == ""):
                continue
        except NoSuchElementException:
            date = "Không có ngày đăng"

        # Lưu thông tin bài báo
        articles.append({
            'title': title,
            'description': description,
            'date': date,
            'url' : url,
        })

# Đóng trình duyệt
driver.quit()

# In ra thông tin bài báo
for article in articles:
    print(f"Tiêu đề: {article['title']}")
    print(f"Tóm tắt: {article['description']}")
    print(f"Ngày đăng: {article['date']}")
    print(f"Url: {article['url']}")
    print("-" * 40)
