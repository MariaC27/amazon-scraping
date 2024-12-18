import json
import csv
import vertexai
from vertexai.generative_models import GenerativeModel


PROJECT_ID = "noxu-dev-marias-team-e4a5f2"
vertexai.init(project=PROJECT_ID, location="us-central1")

# an alternative for the tagging if openai tokens are not enough


def make_gemini_request(text_input):

    model = GenerativeModel("gemini-1.5-pro")

    prompt = f"""
    See the following data in JSON format: {text_input}. The data has info about amazon reviews for a few amazon products.
    Take 50 random samples of 30 reviews each and use these to generate "tags" of commonly used words or
    phrases related to the sentiment towards the product in the reviews. Look at the review rating (out of 5), the title, and
    the review content. Return a list of 12 of these tags. Make sure to include both positive and negative sentiment and context.
    I want the actual output, not a python script. Return ONLY the list of tags, nothing else because I want to write them to a csv file.
    """

    response = model.generate_content(prompt)
    return response


with open('data/all_data.json', 'r') as file:
    data = json.load(file)

text = json.dumps(data, indent=2)
result = make_gemini_request(text)

res = result.text


# write tags to csv
with open('gemini_tags.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['tag'])
    for tag in res:
        writer.writerow([tag])

print("Tags have been written to csv.")
