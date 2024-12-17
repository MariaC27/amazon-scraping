import pandas as pd
import matplotlib.pyplot as plt

# script to visualize frequency of tags in data

# the two csv files generated after tagging
output_info_path = 'data/wb_data/wb_info.csv'
applied_ids_path = 'data/wb_data/tagged_wb_data.csv'

output_info = pd.read_csv(output_info_path)
applied_ids = pd.read_csv(applied_ids_path)

# check structure
# output_info.head(), applied_ids.head()


# join the two datasets on the 'id' column
merged_data = pd.merge(applied_ids, output_info, on='id', how='inner')

# count the frequency of each tag
tag_counts = merged_data['tag'].value_counts()

# generate a bar chart
plt.figure(figsize=(10, 6))
tag_counts.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Frequency of Tags in Amazon Review Data', fontsize=16)
plt.xlabel('Tags', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()


plt.show()
