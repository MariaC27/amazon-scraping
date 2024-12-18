import json
import csv
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')


# for each tag and each object in the JSON, call the API to determine if the tag applies
# generate a CSV file with the ID and the tag for each tag that applies to the object

client = OpenAI(api_key=OPEN_AI_KEY)

with open('data/competitor_data/competitor_data.json', 'r') as file:
    data = json.load(file)


def make_api_request(text_input, tag):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": (
                    f"""
                    For the following review object in JSON format: {text_input}, return true or false about whether the following tag applies to this review with
                    "{tag}". Look at the title, content, and any other attributes of the review to determine if the tag applies
                    (true or false). Return ONLY the word "True" or the word "False", nothing else.
                    """
                )
            }
        ]
    )
    return response


# write header row to tagged_data.csv
with open('tagged_data.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['id', 'tag'])

# get tags from csv file
tags = []
with open('data/tags/gemini_tags.csv', 'r') as tagfile:
    tagreader = csv.reader(tagfile)
    next(tagreader, None)  # skip the header row
    for row in tagreader:
        tags.append(row[0])


for tag in tags:
    skipped_ids = []
    applied_ids = []
    print("starting tag: ", tag)
    for product in data:
        for review in product['reviews']:
            # convert obj to plain text
            text_chunk = json.dumps(review, indent=2)
            result = make_api_request(text_chunk, tag)

            res = result.choices[0].message.content
            review_id = review['id']

            if res == "True":
                applied_ids.append(review_id)
            elif res == "False":
                pass
            else:
                skipped_ids.append(review_id)

    print("skipped ids: ", skipped_ids)
    print("num tagged true: ", len(applied_ids))

    # generates or appends to CSV file with ID and tag in 1:1 relationship, can be joined with another table to make visualizations
    with open('tagged_data.csv', 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for applied_id in applied_ids:
            csvwriter.writerow([applied_id, tag])
