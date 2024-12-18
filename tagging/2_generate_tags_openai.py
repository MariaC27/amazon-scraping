import json
import csv
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')

# call openai API to generate a list of tags based on the JSON data


client = OpenAI(api_key=OPEN_AI_KEY)


def make_api_request(text_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": (
                    f"""
                    See the following data in JSON format: {text_input}. The data has info about amazon reviews for a few amazon products.
                    Take 50 random samples of 30 reviews each and use these to generate "tags" of commonly used words or
                    phrases related to the sentiment towards the product in the reviews. Look at the review rating (out of 5), the title, and
                    the review content. Return a list of 12 of these tags. Make sure to include both positive and negative sentiment and context.
                    I want the actual output, not a python script. Return ONLY the list of tags, nothing else because I want to write them to a csv file.
                    """
                )
            }
        ]
    )
    return response


with open('data/all_data.json', 'r') as file:
    data = json.load(file)

text = json.dumps(data, indent=2)
result = make_api_request(text)

res = result.choices[0].message.content

print("res: ", res)

# remove dash and any extra whitespace
tags = [tag.strip('- .0123456789"').strip() for tag in res.split('\n') if tag.strip()]

with open('tags.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['tag'])
    for tag in tags:
        writer.writerow([tag])

print("Tags have been written to csv.")
