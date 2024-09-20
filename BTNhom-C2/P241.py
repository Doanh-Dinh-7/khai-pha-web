import requests
import json
import re
from bs4 import BeautifulSoup as bs
import time
import dataset
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk import tokenize
import nltk
import matplotlib.pyplot as plt

db = dataset.connect('sqlite:///reviews.db')

review_url = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/'
product_id = '0596158106'  # Cập nhật product_id
session = requests.Session()
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0'
]
session.headers.update({'user-agent': user_agents[0]})

def parse_reviews(reply):
    reviews = []
    try:
        for fragment in reply.split('&&&'):
            if not fragment.strip():
                continue
            json_fragment = json.loads(fragment)
            if json_fragment[0] != 'append':
                continue
            html_soup = bs(json_fragment[2], 'html.parser')
            divs = html_soup.find_all('div', {'data-hook': 'review'})
            for div in divs:
                review_id = div.get('id')
                review_classes = ' '.join(html_soup.find(class_ = 'review-rating').get('class'))
                rating = re.search(r'a-star-(\d+)', review_classes).group(1)
                title = html_soup.find(class_='review-title').get_text(strip=True)
                review = html_soup.find(class_='review-text').get_text(strip=True)
                reviews.append({'review_id': review_id,
                                'rating': rating,
                                'title': title,
                                'review': review})
    except Exception as e:
        print(f"Error parsing reviews: {e}")
    return reviews

def get_reviews(product_id, page):
    data = {
        'sortBy': '',
        'reviewerType': 'all_reviews',
        'formatType': '',
        'mediaType': '',
        'filterByStar': 'all_stars', 
        'pageNumber': page,
        'filterByKeyword': '',
        'shouldAppend': 'undefined',
        'deviceType': 'desktop',
        'reftag': 'cm_cr_arp_d_paging_btm_next_{}'.format(page),
        'pageSize': 10,  
        'asin': product_id,
        'scope': 'reviewsAjax0'  
    }
    headers = {'user-agent': user_agents[page % len(user_agents)]}
    session.headers.update(headers)

    for attempt in range(5):  # Thử lại tối đa 5 lần
        try:
            response = session.post(review_url, data=data)
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            if "BAAAAAD ASIN!" in response.text:
                print("Error: Bad ASIN or incorrect URL.")
                break
            reviews = parse_reviews(response.text)
            if reviews:
                return reviews
        except requests.RequestException as e:
            print(f"Request error: {e}")
        time.sleep(5)  # Chờ trước khi thử lại
    return []

def scraped_reviews():
    page = 1
    while True:
        print("Scraping page", page)
        reviews = get_reviews(product_id, page)
        if not reviews:
            break
        for review in reviews:
            print(' -', review['rating'], review['title'])
            db['reviews'].upsert(review, ['review_id'])
        page += 1

def Analysis_db():
    # Tải punkt nếu chưa có
    nltk.download('punkt')

    reviews = db['reviews'].all()
    analyzer = SentimentIntensityAnalyzer()
    sentiment_by_stars = [[] for r in range(1, 6)]

    for review in reviews:
        full_review = review['title'] + '. ' + review['review']
        sentence_list = tokenize.sent_tokenize(full_review)
        cumulative_sentiment = 0.0
        for sentence in sentence_list:
            vs = analyzer.polarity_scores(sentence)
            cumulative_sentiment += vs["compound"]
        if len(sentence_list) > 0:
            average_score = cumulative_sentiment / len(sentence_list)
            sentiment_by_stars[int(review['rating']) - 1].append(average_score)

    # Loại bỏ các danh sách con rỗng
    sentiment_by_stars = [s for s in sentiment_by_stars if s]

    # Kiểm tra xem có dữ liệu để vẽ không
    if any(sentiment_by_stars):
        plt.violinplot(sentiment_by_stars,
                    range(1, len(sentiment_by_stars) + 1),
                    vert=False, widths=0.9,
                    showmeans=False, showextrema=True, showmedians=True,
                    bw_method='silverman')
        plt.axvline(x=0, linewidth=1, color='black')
        plt.show()
    else:
        print("Không có dữ liệu để vẽ biểu đồ.")


if  __name__ == "__main__":
    scraped_reviews()
    Analysis_db()
    



