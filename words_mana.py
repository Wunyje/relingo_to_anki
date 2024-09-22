#%% md
# 
#%% md
# ## Requirements
# - Input with `.csv` files, which start with `relingo` and output `.txt` files with specific formats:
#   - The `.csv`'s columns include 'word', 'translation','phonetic','mastered','sentences'.
#   - Remove the 'mastered' column, keep other columns, and rearrange the content in the csv into format like:
#   ```
#     *word1 
#     **phonetic1 
#     ====================================
#     1. translation1.1
#     2. translation1.2
#     3. translation1.3
#     ...
#     x. translation1.x
#     ====================================
#     1. sentences1.1
#     2. sentences1.2
#     ...
#     y. sentences1.y
# 
#     *word2 
#     **phonetic2 
#     ====================================
#     translation2 
#     ...
#     ====================================
#     sentences2
#     ...
# 
#     ...... 
# 
#     *wordn 
#     **phoneticn 
#     ====================================
#     translationn
#     ...
#     ====================================
#     sentencesn
#     ...
#   ```
#   - If the `translation`'s content has multiple rows, only keep the first row of it. And if the 'translation' and 'sentences' have multiple of them, which could be divided by ';', then split them into different rows and add corresponding serial number.
# - Select out newly added words
#   - The `.csv` would contain old words, create `added_words.txt` to compare with each time, select only 'word' column's content to save in after selecting out those new words to `new_words.txt`.
# 
#%%
import os
import re
import pandas as pd

def process_csv(file_path, added_words_file='added_words.txt'):
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Remove the 'mastered' column and rearrange the columns
    df = df.drop(columns=['mastered'])
    df = df[['word', 'translation', 'phonetic', 'sentences']]

     # Only keep the first row of the 'translation' content if it has multiple rows
    df['translation'] = df['translation'].apply(lambda x: x.split('\n')[0] if isinstance(x, str) else x)

    # Function to rearrange 'translation' content
    # Function to rearrange 'translation' content
    def rearrange_translation(text):
        if isinstance(text, str):
            # Use a regular expression to match word classes and split accordingly
            parts = re.split(r'((?:NOUN|VERB|ADJ|ADV)\.)', text)
            result = []
            count = 1  # Initialize count
            
            for i in range(len(parts)):
                part = parts[i].strip()
                if not part:
                    continue
                # If the part is a word class, add it without numbering
                if re.match(r'^(NOUN|VERB|ADJ|ADV)\.$', part):
                    result.append(part)  # Add the word class as a new line
                    count = 1  # Reset numbering for a new word class
                else:
                    # Split the following content on delimiters and add numbering
                    sub_parts = re.split(r'[；;，]', part)
                    for sub_part in sub_parts:
                        result.append(f"{count}. {sub_part.strip()}")
                        count += 1
                        
            return '\n'.join(result)
        return text
    
    df['translation'] = df['translation'].apply(rearrange_translation)
    
    # Split 'sentences' on ';' and add serial numbers
    def split_and_number(text):
        if isinstance(text, str):
            parts = text.split(';')
            return '\n'.join([f"{i+1}. {part.strip()}" for i, part in enumerate(parts)])
        return text
    
    df['sentences'] = df['sentences'].apply(split_and_number)
    
    # Check if the added_words.txt exists
    if os.path.exists(added_words_file):
        with open(added_words_file, 'r', encoding='utf-8') as f:
            old_words = f.read().splitlines()
    else:
        old_words = []
    
    # Find new words
    new_words_df = df[~df['word'].isin(old_words)]
    
    # Prepare the output format for new words
    output_lines = []
    for _, row in new_words_df.iterrows():
        # Convert each value to string and handle missing values by replacing NaN with an empty string
        word = str(row['word']) if not pd.isna(row['word']) else ""
        phonetic = str(row['phonetic']) if not pd.isna(row['phonetic']) else ""
        translation = str(row['translation']) if not pd.isna(row['translation']) else ""
        sentences = str(row['sentences']) if not pd.isna(row['sentences']) else ""

        # Append the formatted strings to output_lines
        output_lines.append(f"*{word}")
        output_lines.append(f"**{phonetic}")
        output_lines.append("==================")
        output_lines.append(translation)
        output_lines.append("==================")
        output_lines.append(sentences)
        output_lines.append("\n")
        
    # Save the new words' data to new_words.txt
    if output_lines:
        with open('new_words.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print("New words found and formatted data saved to new_words.txt")
    
    # Append the new words to added_words.txt
    with open(added_words_file, 'a', encoding='utf-8') as f:
        for word in new_words_df['word']:
            f.write(f"{word}\n")
    
    print(f"Updated {added_words_file} with the latest words.")
    

# Example of how to use the function
input_directory = '.'  # Change to your directory

for file_name in os.listdir(input_directory):
    if file_name.startswith('relingo') and file_name.endswith('.csv'):
        process_csv(os.path.join(input_directory, file_name))
