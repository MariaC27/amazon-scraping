import json
import csv

# assumes we already have a json with the amazon data from previous scraping
# now loading reviews from json data into a csv table so it can be joined with tagged data later

with open('wb_data.json', 'r') as json_file:
    data = json.load(json_file)

with open('wb_info.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['id', 'product', 'product_asin', 'review_title', 'rating', 'date', 'location', 'flavor', 'size', 'type'])

    for element in data:
        # extract the reviews
        product = element.get('title')
        asin = element.get('asin')

        # iterate through each review in the reviews list
        for review in element.get('reviews', []):
            writer.writerow([
                review.get('id'),
                product,
                asin,
                review.get('title'),
                review.get('rating'),
                review.get('date'),
                review.get('location'),
                review.get('flavor'),
                review.get('size'),
                review.get('type')
            ])

print("CSV info file has been created successfully.")
