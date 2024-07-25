import cv2
import os
import hashlib

# Create mappings for character to ASCII and vice versa
char_to_num = {chr(i): i for i in range(256)}
num_to_char = {i: chr(i) for i in range(256)}

# Function to read an image
def read_image(file_path):
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {file_path}. Please check the path.")
    return img

# Function to save and open the modified image
def save_and_open_image(img, save_path):
    cv2.imwrite(save_path, img)
    print(f"Data successfully hidden in image. Saved as {save_path}.")
    os.startfile(save_path)

# Hash the key for security
def generate_hashed_key(key):
    return hashlib.sha256(key.encode()).digest()

# Function to embed text into the image
def embed_text(img, text, key):
    rows, cols, _ = img.shape
    hashed_key = generate_hashed_key(key)
    key_len = len(hashed_key)
    text_len = len(text)
    idx = 0
    channel = 0  # BGR channel

    # Embed the length of the text
    text_len_str = str(text_len).zfill(8)  # Ensure it's 8 digits long
    text = text_len_str + text

    for char in text:
        r = (idx // cols) % rows
        c = idx % cols
        img[r, c, channel] = char_to_num[char] ^ hashed_key[idx % key_len]
        channel = (channel + 1) % 3
        idx += 1

    return img

# Function to extract text from the image
def extract_text(img, key):
    rows, cols, _ = img.shape
    hashed_key = generate_hashed_key(key)
    key_len = len(hashed_key)
    idx = 0
    channel = 0  # BGR channel
    decoded_text = ""
    text_len_str = ""

    # Extract the length of the text first
    for _ in range(8):
        r = (idx // cols) % rows
        c = idx % cols
        decrypted_char = num_to_char[img[r, c, channel] ^ hashed_key[idx % key_len]]
        text_len_str += decrypted_char
        channel = (channel + 1) % 3
        idx += 1
    
    text_len = int(text_len_str)

    # Extract the actual text
    for _ in range(text_len):
        r = (idx // cols) % rows
        c = idx % cols
        decrypted_char = num_to_char[img[r, c, channel] ^ hashed_key[idx % key_len]]
        decoded_text += decrypted_char
        channel = (channel + 1) % 3
        idx += 1

    return decoded_text

def main():
    try:
        file_path = input("Enter the image file path: ")
        img = read_image(file_path)

        key = input("Enter the security key: ")
        hidden_text = input("Enter the text to hide: ")

        # Encode the text in the image
        modified_img = embed_text(img, hidden_text, key)
        save_path = "hidden_image.png"
        save_and_open_image(modified_img, save_path)

        # Prompt user to decode the text
        if input("\nEnter '1' to extract data from the image: ") == '1':
            reentered_key = input("\nRe-enter the key to decode the text: ")
            if key == reentered_key:
                try:
                    extracted_text = extract_text(modified_img, reentered_key)
                    print(f"\nThe hidden text is:\n{extracted_text}")
                except Exception as error:
                    print(f"Error during decoding: {error}")
            else:
                print("Keys do not match. Cannot decode the text.")
        else:
            print("Exiting.")
    
    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
