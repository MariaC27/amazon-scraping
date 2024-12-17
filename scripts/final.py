from bs4 import BeautifulSoup
import json
import requests
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()


# Script to scrape product data from the main page of an amazon product, and also scrape reviews from subsequent pages of reviews


# returns the soup for a given url
def get_page(url):
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.amazon.com/',
    }
    # add cookies so can authenticate past 2nd reviews page
    session.cookies.set('session-id', os.getenv('SESSION_ID'), domain='.amazon.com')
    session.cookies.set('ubid-main', os.getenv('UBID_MAIN'), domain='.amazon.com')
    session.cookies.set('x-main', os.getenv('X_MAIN'), domain='.amazon.com')
    try:
        res = session.get(url)
        html = res.text
        return BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None


# returns a dict with title, rating, number of ratings, distribution of ratings from main page
# main page URLs should be of format: https://www.amazon.com/dp/{asin}
def get_product_info(asin):
    url = f'https://www.amazon.com/dp/{asin}'
    soup = get_page(url)
    if not soup:
        print("no soup found")
        return None

    product_data = {}
    product_data["asin"] = asin
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

    return product_data


# gets reviews by iterating through all pages of reviews
# Review urls should be of format:
# https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_viewopt_srt?sortBy=recent&filterByStar={star}&pageNumber={num}
def get_reviews(asin):
    page = 1
    reviews = []
    star_list = ["five_star", "four_star", "three_star", "two_star", "one_star"]
    review_counts = {
        "five_star": 0,
        "four_star": 0,
        "three_star": 0,
        "two_star": 0,
        "one_star": 0
    }
    for star in star_list:
        while page <= 10:  # amazon only loads 10 pages of reviews for each star
            url = f'https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&filterByStar={star}&pageNumber={page}'
            soup = get_page(url)
            if soup:
                review_content = soup.find_all("div", {"data-hook": "review"})
                for review in review_content:
                    star_rating = review.find("span", {"class": "a-icon-alt"}).get_text().replace(" out of 5 stars", "")
                    title_element = review.find("a", {"data-hook": "review-title"}).get_text().strip()
                    title = title_element.split("out of 5 stars")[-1].strip()
                    content = review.find("span", {"data-hook": "review-body"}).get_text().strip()
                    # get and split date and location of purchase
                    date_string = review.find("span", {"data-hook": "review-date"}).get_text().strip().replace("Reviewed in ", "")
                    location, date = date_string.split(" on ")
                    location = location.replace("the ", "").strip()  # removes "the" if it exists from the location

                    # get and split flavor and size
                    flavor = ""  # defaults to empty string
                    size = ""
                    details = review.find("a", {"data-hook": "format-strip"})
                    if details:
                        details = details.get_text().strip()
                        if "Size:" in details:
                            flavor, size = details.split("Size:")
                        else:
                            flavor = details

                    # get helpfulness upvotes and type of purchase (verified vs. free product)
                    helpful = review.find("span", {"data-hook": "helpful-vote-statement"})
                    if helpful:
                        helpful = helpful.get_text().strip()
                    else:
                        helpful = ""

                    type = ""
                    verified = review.find("span", {"data-hook": "avp-badge"})
                    review_strip = review.find("div", {"class": "a-row a-spacing-mini review-data review-format-strip"})
                    vine = "Vine Customer Review" in review_strip.get_text().strip()
                    if verified:
                        type = verified.get_text().strip()
                    elif vine:
                        type = "Amazon Vine Customer Review of Free Product"

                    review_data = {
                        'id': hashlib.md5(f'{asin}_{star_rating}_{date}_{location}_{content}'.encode()).hexdigest(),
                        'rating': star_rating,
                        'title': title,
                        'content': content,
                        'date': date,
                        'location': location,
                        'flavor': flavor.replace("Flavor Name:", "").strip(),
                        'size': size.strip(),
                        'helpful': helpful,
                        'type': type
                    }
                    reviews.append(review_data)
                    review_counts[star] += 1
                page += 1
            else:
                print("next page not found")
                break
        page = 1  # reset page for next star
    print("review counts: ", review_counts)
    return reviews


# generate data for each asin
def generate_data(asin):
    product_data = get_product_info(asin)
    if not product_data:
        print("no product data found")
        return None
    reviews = get_reviews(asin)
    product_data["reviews"] = reviews
    return product_data


asins = ['B0BCX8P7LL', 'B0C67N355H', 'B0CX44G88R']  # HERE modify list of ASINs to scrape

all_products = []
for asin in asins:
    product_data = generate_data(asin)
    if product_data:
        all_products.append(product_data)

with open('amazon_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_products, f, indent=4, ensure_ascii=False)

print("JSON file created successfully.")
