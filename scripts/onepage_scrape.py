from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import json


# Script to scrape product data from the main page of an amazon product


def get_page(url, headers):
    try:
        req = Request(url, headers=headers)
        webpage = urlopen(req)
        return BeautifulSoup(webpage, "html.parser")
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None


def get_product_info(soup):
    product_data = {}
    # get title
    title_element = soup.find("h1", {"id": "title"})
    if title_element:
        title = title_element.find("span", {"id": "productTitle"}).get_text(strip=True)
        product_data["title"] = title
    else:
        product_data["title"] = ""
        print("no title element found")

    # get rating
    rating_element = soup.find("span", {"data-hook": "rating-out-of-text"})
    if rating_element:
        rating = rating_element.get_text(strip=True)
        rating = rating.replace(" out of 5", "")
        product_data["rating"] = rating
    else:
        product_data["rating"] = ""
        print("no rating element found")

    # get number of ratings
    number_of_ratings_element = soup.find("span", {"data-hook": "total-review-count"})
    if number_of_ratings_element:
        number_of_ratings = number_of_ratings_element.get_text(strip=True)
        number_of_ratings = number_of_ratings.replace(" global ratings", "")
        product_data["number_of_ratings"] = number_of_ratings
    else:
        product_data["number_of_ratings"] = ""
        print("no number of ratings element found")

    # get distribution of ratings
    distributionlist = soup.find_all("span", {"class": "_cr-ratings-histogram_style_histogram-column-space__RKUAd"})
    distribution = {}
    for i, item in enumerate(distributionlist[5:10], start=5):
        stars = 10 - i  # Convert index to star rating (5,4,3,2,1)
        percentage = item.get_text(strip=True)
        distribution[str(stars)] = percentage
    product_data["distribution"] = distribution

    # get ASIN
    asin = re.search(r'/[dg]p/([^/]+)', url, flags=re.IGNORECASE)
    if asin:
        product_data["asin"] = asin.group(1)
    else:
        product_data["asin"] = ""
        print("no ASIN found")

    return product_data


def get_reviews(soup):
    reviews = []
    review_content = soup.find_all("div", {"data-hook": "review"})
    for review in review_content:
        review_data = {
            'rating': review.find("span", {"class": "a-icon-alt"}).get_text(),
            'content': review.find("span", {"data-hook": "review-body"}).get_text().strip()
        }
        reviews.append(review_data)
    return reviews


url = "https://www.amazon.com/dp/B0BCX8P7LL/?th=1"


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}


def generate_data(url):
    soup = get_page(url, headers)

    if soup:
        product_data = get_product_info(soup)
        reviews = get_reviews(soup)
        product_data["reviews"] = reviews
        return product_data
    else:
        print("no soup found")
        return None


urls = [
    "https://www.amazon.com/dp/B0BCX8P7LL/?th=1",
    "https://www.amazon.com/dp/B0CX4NYH83/?th=1",
    "https://www.amazon.com/dp/B0C67N355H/?th=1",
]

all_products = []
for url in urls:
    product_data = generate_data(url)
    if product_data:
        all_products.append(product_data)

with open('amazon_product_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_products, f, indent=4, ensure_ascii=False)

print("JSON file created successfully.")
