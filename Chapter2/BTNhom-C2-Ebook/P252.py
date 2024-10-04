import dataset
db = dataset.connect('sqlite:///news_articles.db')  # Use SQLite database; change URI for other databases

def scraping_news_articles():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from bs4 import BeautifulSoup
    import time
    
    # Turn off unnecessary error messages
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")
    
    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the Google News top stories page
    driver.get('https://news.google.com/topstories')

    # Wait for the page to load fully
    time.sleep(5)  # Increased waiting time to ensure page content is fully loaded

    # Get page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Initialize the database
    db = dataset.connect('sqlite:///news_articles.db')  # Use SQLite database; change URI for other databases
    articles_table = db['articles']

    # Find all articles
    articles = soup.find_all('article')

    # Extract headlines, URLs, and content
    for article in articles:
        # Find the <a> tag with the class "gPFEn" which contains the title and URL
        link_tag = article.find('a', class_='gPFEn')
        if link_tag:
            title = link_tag.get_text(strip=True)
            link = 'https://news.google.com' + link_tag['href'][1:]

            # Visit each article link to extract content
            driver.get(link)
            time.sleep(10)  # Wait for the page to load

            # Get page source and parse with BeautifulSoup
            article_soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract the main content of the article
            paragraphs = article_soup.find_all('p')
            content = ' '.join([para.get_text() for para in paragraphs])
            
            # Insert data into the database
            articles_table.insert({
                'title': title,
                'link': link,
                'content': content
            })

            print(f'Title: {title}')
            print(f'Link: {link}')
            print(f'Content: {content[:500]}...')  # Print the first 500 characters for brevity
            print()  # Print a newline for better readability

    # Close the WebDriver
    driver.quit()

def analyzing_news_articles():
    from nltk.tokenize import RegexpTokenizer
    from nltk.stem.porter import PorterStemmer
    from stop_words import get_stop_words
    
    articles = []

    tokenizer = RegexpTokenizer(r'\w+')
    stop_words = get_stop_words('en')
    p_stemmer = PorterStemmer()

    for article in db['articles'].all():
        text = article['title'].lower().strip()
        text += " " + article['content'].lower().strip()
        if not text:
            continue
        # Tokenize
        tokens = tokenizer.tokenize(text)
        # Remove stop words and small words
        clean_tokens = [i for i in tokens if not i in stop_words]
        clean_tokens = [i for i in clean_tokens if len(i) > 2]
        # Stem tokens
        stemmed_tokens = [p_stemmer.stem(i) for i in clean_tokens]
        # Add to list
        articles.append((article['title'], stemmed_tokens))

    print(articles[0])

    from gensim import corpora
    dictionary = corpora.Dictionary([a[1] for a in articles])
    corpus = [dictionary.doc2bow(a[1]) for a in articles]

    print(corpus[0])

    from gensim.models.ldamodel import LdaModel
    nr_topics = 5
    ldamodel = LdaModel(corpus, num_topics=nr_topics, 
                        id2word=dictionary, passes=20)

    print(ldamodel.print_topics())

    # Show topics by top-3 terms
    for t in range(nr_topics):
        print(ldamodel.print_topic(t, topn=3))

    # Show some random articles
    from random import shuffle
    idx = list(range(len(articles)))
    shuffle(idx)
    for a in idx[:3]:
        article = articles[a]
        print('==========================')
        print(article[0])
        prediction = ldamodel[corpus[a]][0]
        print(ldamodel.print_topic(prediction[0], topn=3))
        print('Probability:', prediction[1])
        
if __name__ == '__main__':
    scraping_news_articles()
    analyzing_news_articles()
