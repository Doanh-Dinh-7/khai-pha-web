import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# Thiết lập trình duyệt
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Danh sách để lưu các link
links = []

for page in range(1, 168):
    url = f"https://baodaklak.vn/khoa-hoc-cong-nghe/?paged={page}"
    driver.get(url)

    # Cào các thẻ a với class 'title1' hoặc 'title1 photo'
    elements = driver.find_elements(By.CSS_SELECTOR, "a.title1, a.title1.photo")
    
    for element in elements:
        href = element.get_attribute('href')
        if href in links:
            continue
        links.append(href)

# Đóng trình duyệt
driver.quit()

with open('Cau2.txt', 'w', encoding='utf-8') as file:
    # In ra danh sách các link
    for link in links:
        file.write(link + '\n')