import pytesseract
from PIL import Image
import logging
from Scripts.process_image import preprocess_image_to_bw


def extract_text_from_image(image_file):
    # Preprocesar la imagen a blanco y negro (binarización)
    # bw_image = preprocess_image_to_bw(image_file)
    image = Image.open(image_file)
    # custom_config = r'--oem 3 --psm 6'
    # custom_config = r'--oem 3'
    # extracted_text = pytesseract.image_to_string(bw_image, config=custom_config)
    extracted_text = pytesseract.image_to_string(image)
    # extracted_text = pytesseract.image_to_string(bw_image)
    logging.debug(f"Texto extraído de la imagen: {extracted_text}")
    return extracted_text