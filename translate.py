from PIL import Image, ImageDraw, ImageFont

# Load the image
image_path = "images/hello.png"
image = Image.open(image_path)
draw = ImageDraw.Draw(image)
font_path="TiroDevanagariHindi-Regular.ttf"
# Use the default PIL font
font = ImageFont.truetype(font_path,70)

# Original sentences and their translated versions
original_sentences = ['Food production - Soil and Water management', 'Introduction']
translated_sentences = ['अन्न उत्पादन - माती आणि पाणी व्यवस्थापन', 'परिचय']

# Coordinates for each word
word_coordinates = [
    {"text":"Food","confidence":96,"coordinates":[151,38,304,99]},
    {"text":"production","confidence":93,"coordinates":[333,38,686,116]},
    {"text":"-","confidence":93,"coordinates":[713,72,736,79]},
    {"text":"Soil","confidence":96,"coordinates":[765,38,884,97]},
    {"text":"and","confidence":96,"coordinates":[912,38,1025,98]},
    {"text":"Water","confidence":95,"coordinates":[1054,41,1268,99]},
    {"text":"management","confidence":95,"coordinates":[1295,45,1703,115]},
    {"text":"Introduction","confidence":92,"coordinates":[144,187,417,231]}
]

# Function to find coordinates of the first and last words
def get_bounding_box(sentence, word_coordinates):
    words = sentence.split()
    first_word = words[0]
    last_word = words[-1]

    first_coord = None
    last_coord = None

    for coord in word_coordinates:
        if coord["text"] == first_word and not first_coord:
            first_coord = coord["coordinates"]
        if coord["text"] == last_word:
            last_coord = coord["coordinates"]
    
    if first_coord and last_coord:
        min_x = first_coord[0]
        min_y = first_coord[1]
        max_x = last_coord[2]
        max_y = last_coord[3]
        return (min_x, min_y, max_x, max_y)
    else:
        return None

# Replace each sentence with the translated text
for i, original_sentence in enumerate(original_sentences):
    print(translated_sentences[i]+"---")
    bounding_box = get_bounding_box(original_sentence, word_coordinates)
    if bounding_box:
        draw.rectangle(bounding_box, fill="white")  # Fill the bounding box with white color to cover the old text
        draw.text((bounding_box[0], bounding_box[1]), translated_sentences[i], font=font, fill="black")  # Draw the new text

# Save the edited image
output_path = "path_to_save_edited_image.png"
image.save(output_path)
