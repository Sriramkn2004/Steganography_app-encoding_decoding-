from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from PIL import Image
import os
from django.conf import settings
def home(request):
    return render(request, 'steganography/home.html')

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from PIL import Image
import os
from io import BytesIO
from django.conf import settings

def encode_image(request):
    if request.method == 'POST' and request.FILES['image'] and request.POST['message']:
        # Get the uploaded image and the message
        image = request.FILES['image']
        message = request.POST['message']

        # Save the image to a temporary file in the media folder
        fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'media'))
        img_path = fs.save('temp_image.png', image)  # Save it under the media folder
        img_url = fs.url(img_path)  # URL for accessing the image

        # Open the image using PIL
        img = Image.open(os.path.join(settings.BASE_DIR, 'media', img_path))  # Correctly access the saved image

        # Convert the message to binary format
        binary_message = ''.join(format(ord(i), '08b') for i in message)  # Convert the message to binary

        # Get the image data (pixels)
        img_data = img.getdata()

        # Encode the message in the LSB (Least Significant Bit) of the pixels
        new_data = []
        message_index = 0
        for pixel in img_data:
            new_pixel = list(pixel)
            for i in range(3):  # For RGB channels
                if message_index < len(binary_message):
                    new_pixel[i] = new_pixel[i] & ~1 | int(binary_message[message_index])  # LSB modification
                    message_index += 1
            new_data.append(tuple(new_pixel))
            if message_index >= len(binary_message):
                break

        # Apply the modified pixels to the image
        img.putdata(new_data)

        # Save the new encoded image to memory (using BytesIO)
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)  # Seek to the beginning of the file to save it properly

        # Save the new encoded image in the media folder
        encoded_img_path = fs.save('encoded_image.png', img_io)
        encoded_img_url = fs.url(encoded_img_path)

        return render(request, 'steganography/encode.html', {
            'img_url': img_url, 
            'encoded_img_url': encoded_img_url
        })

    return render(request, 'steganography/encode.html')

def encode_message(img, message):
    # Example encoding function: encoding the message in the least significant bits of the image
    binary_message = ''.join(format(ord(i), '08b') for i in message)
    img_data = img.getdata()
    new_img_data = []

    binary_index = 0
    for pixel in img_data:
        r, g, b = pixel
        if binary_index < len(binary_message):
            r = r & 0xFE | int(binary_message[binary_index])
            binary_index += 1
        new_img_data.append((r, g, b))

    img.putdata(new_img_data)
    return img

def decode_message_from_image(img):
    # Convert the image into a list of pixels
    img_data = img.getdata()

    # Collect the binary message
    binary_message = ''
    for pixel in img_data:
        for i in range(3):  # RGB channels
            binary_message += str(pixel[i] & 1)  # Extract the LSB

    # Assume the message is encoded with a specific ending delimiter, like '00000000'
    # Find where the message ends (look for the 8 zeros or another delimiter)
    end_index = binary_message.find('00000000')
    if end_index != -1:
        binary_message = binary_message[:end_index]  # Get the binary message up until the delimiter
    
    # Split the binary message into chunks of 8 (1 byte) and convert to text
    message = ''
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        if len(byte) == 8:  # Ensure we're working with complete bytes
            message += chr(int(byte, 2))

    # Return the decoded message
    return message
def decode_image(request):
    if request.method == 'POST' and request.FILES['image']:
        # Get the uploaded image
        image = request.FILES['image']

        # Save the image to the media directory
        fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'media'))
        img_path = fs.save('temp_image_to_decode.png', image)  # Save it in the media folder
        img_url = fs.url(img_path)  # URL to access the image

        # Now, open the image using PIL
        img = Image.open(os.path.join(settings.BASE_DIR, 'media', img_path))

        # Decoding logic here...
        decoded_message = decode_message_from_image(img)

        return render(request, 'steganography/decode.html', {
            'img_url': img_url, 
            'decoded_message': decoded_message
        })

    return render(request, 'steganography/decode.html')