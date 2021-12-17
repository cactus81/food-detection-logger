import io
import os
import cv2
from google.cloud import vision_v1p3beta1 as vision

# Setup google authentication client key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_key.json'

# Source path for images
SOURCE_PATH = "/Users/jkakstys/PycharmProjects/FrDetect/photos/"

# Setup camera
cap = cv2.VideoCapture(0)


# Import list of all possible foods
def load_food_name():
    names = [line.rstrip('\n').lower() for line in open('Groceries.dict')]
    return names


# Resize image using OpenCV and identify using Google Vision
def recognize_food(img_path, food_list):
    # Read image with opencv
    img = cv2.imread(img_path)

    # Get image size
    height, width = img.shape[:2]

    # Scale image
    img = cv2.resize(img, (800, int((height * 800) / width)))

    # Save the image to temp file
    cv2.imwrite(SOURCE_PATH + "output.jpg", img)

    # Create new img path for google vision
    img_path = SOURCE_PATH + "output.jpg"

    # Create google vision client
    client = vision.ImageAnnotatorClient()

    # Read image file
    with io.open(img_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    # Recognize text
    response = client.label_detection(image=image)
    labels = response.label_annotations

    # Search food catalog for returned Google keywords
    for label in labels:
        desc = label.description.lower()

        if desc in food_list:
            return desc


# Main function used to catalog ingredients
list_foods = load_food_name()
path = SOURCE_PATH + 'img_capture.jpg'
ingredients = {}

# Clear the screen
if os.name == 'posix':
    os.system('clear')
else:
    os.system('cls')

print("""Instructions: 
Press 'a' to Add item to list
Press 'l' to List all items
""")
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # Capture image from camera and send to Google Vision for analysis.
    # Then prompt user to input item weight.
    if cv2.waitKey(1) & 0xFF == ord('a'):
        cv2.imwrite(path, frame)
        current_ingredient = recognize_food(path, list_foods)
        current_weight = float(input(f'How many grams does the {current_ingredient} weigh? '))

        # Adds the current ingredient to dictionary if it isn't there
        # or updates the total weight if ingredient was previously logged
        if current_ingredient in ingredients:
            ingredients[current_ingredient] += current_weight
        else:
            ingredients[current_ingredient] = current_weight

    # End recognition loop when L is pressed
    elif cv2.waitKey(1) & 0xFF == ord('l'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

# Print ingredients list
print("""

------------------------
List of all ingredients
------------------------
""")
for name, weight in ingredients.items():
    print(f'You have {weight} grams of {name}s.')

print("Let's cook!")
