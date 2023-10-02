# -*- coding: utf-8 -*-
"""
Created on Tue Mar 1 18:51:22 2022

@author: suraj
"""
import streamlit as st
from streamlit_cropper import st_cropper
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont
from urllib.request import urlopen
import os
import base64
import io
from io import BytesIO

Output_image = 500


def main():
    @st.cache
    def load_image(url):
        with urlopen(url) as response:
            image = np.asarray(bytearray(response.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = image[:, :, [2, 1, 0]]  # BGR -> RGB
        return image

    image = load_image('https://raw.githubusercontent.com/rafaelgrecco/Filter-Selector/master/Images/placeholder.jpg')
    image = Image.fromarray(image)
    st.title('SnapEdit')
    st.sidebar.title('Sidebar')

    menu = ['Filters', 'Image Corrections', 'Tools', 'Image Rotation', 'Add Text to Image', 'Information']
    op = st.sidebar.selectbox('Option', menu)
    img = None
    realtime_update = True  # You can set the default value to True or False as per your preference
    box_color = '#0000FF'
    aspect_ratio = None
    if op == 'Tools':
        st.set_option('deprecation.showfileUploaderEncoding', False)

        # Upload an image and set some options for demo purposes

        img = st.file_uploader('Upload an image', type=['jpg', 'png', 'jpeg'])

        realtime_update = st.sidebar.checkbox(label="Update in Real Time", value=True)
        box_color = st.sidebar.color_picker(label="Box Color", value='#0000FF')
        aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=["1:1", "16:9", "4:3", "2:3", "Free"])
        aspect_dict = {
            "1:1": (1, 1),
            "16:9": (16, 9),
            "4:3": (4, 3),
            "2:3": (2, 3),
            "Free": None
        }
        aspect_ratio = aspect_dict[aspect_choice]

        if img:
            img = Image.open(img)
            if not realtime_update:
                st.write("Double click to save crop")
            # Get a cropped image from the frontend
            cropped_img = st_cropper(img, realtime_update=realtime_update, box_color=box_color,
                                     aspect_ratio=aspect_ratio)

            # Manipulate cropped image at will
            st.write("Preview")
            _ = cropped_img.thumbnail((150, 150))
            st.image(cropped_img)

    if op == 'Filters':

        img = st.file_uploader('Upload an image', type=['jpg', 'png', 'jpeg'])

        if img is not None:
            image = Image.open(img)
            st.sidebar.text('Original Image')
            st.sidebar.image(image, width=200)

        filters = st.sidebar.radio('Filters', ['Original', 'Grayscale', 'Sepia', 'Blur', 'Contour', 'Sketch'])

        if filters == 'Grayscale':
            img_convert = np.array(image.convert('RGB'))
            gray_image = cv2.cvtColor(img_convert, cv2.COLOR_RGB2GRAY)
            st.image(gray_image, width=Output_image)








        elif filters == 'Sepia':
            img_convert = np.array(image.convert('RGB'))
            img_convert = cv2.cvtColor(img_convert, cv2.COLOR_RGB2BGR)
            kernel = np.array([[0.272, 0.534, 0.131],
                               [0.349, 0.686, 0.168],
                               [0.393, 0.769, 0.189]])
            sepia_image = cv2.filter2D(img_convert, -1, kernel)
            st.image(sepia_image, channels='BGR', width=Output_image)

        elif filters == 'Blur':
            img_convert = np.array(image.convert('RGB'))
            slide = st.sidebar.slider('Quantidade de Blur', 3, 81, 9, step=2)
            img_convert = cv2.cvtColor(img_convert, cv2.COLOR_RGB2BGR)
            blur_image = cv2.GaussianBlur(img_convert, (slide, slide), 0, 0)
            st.image(blur_image, channels='BGR', width=Output_image)

        elif filters == 'Contour':
            img_convert = np.array(image.convert('RGB'))
            img_convert = cv2.cvtColor(img_convert, cv2.COLOR_RGB2BGR)
            blur_image = cv2.GaussianBlur(img_convert, (11, 11), 0)
            canny_image = cv2.Canny(blur_image, 100, 150)
            st.image(canny_image, width=Output_image)

        elif filters == 'Sketch':
            img_convert = np.array(image.convert('RGB'))
            gray_image = cv2.cvtColor(img_convert, cv2.COLOR_RGB2GRAY)
            inv_gray = 255 - gray_image
            blur_image = cv2.GaussianBlur(inv_gray, (25, 25), 0, 0)
            sketch_image = cv2.divide(gray_image, 255 - blur_image, scale=256)
            st.image(sketch_image, width=Output_image)
        else:
            st.image(image, width=Output_image)

    if op == 'Image Rotation':
        st.set_option('deprecation.showfileUploaderEncoding', False)

        img = st.file_uploader('Upload an image', type=['jpg', 'png', 'jpeg'])

        rotation_angle = st.slider('Rotation Angle', -180, 180, 0)

        if img:
            img = Image.open(img)
            if not realtime_update:
                st.write("Double click to save crop")

            # Rotate the image based on the user's selection
            rotated_img = img.rotate(rotation_angle, resample=Image.BICUBIC, expand=True)

            # Get a cropped image from the frontend
            cropped_img = st_cropper(rotated_img, realtime_update=realtime_update, box_color=box_color,
                                     aspect_ratio=aspect_ratio)

            # Manipulate cropped image at will
            st.write("Preview")
            _ = cropped_img.thumbnail((150, 150))
            st.image(cropped_img)
    if op == 'Add Text to Image':
        st.set_option('deprecation.showfileUploaderEncoding', False)

        img = st.file_uploader('Upload an image', type=['jpg', 'png', 'jpeg'])

        if img:
            img = Image.open(img)
            st.write("Original Image")
            st.image(img, use_column_width=True, channels='RGB')

            # Get user input for text to add to the image
            text_to_add = st.text_input('Enter text to add:', '')

            # Get user input for text size
            text_size = st.slider('Text Size', 10, 100, 30)  # Adjust the range and default values as needed

            # Get user input for X and Y coordinates
            text_x = st.slider('X Coordinate', 0, img.width,
                               img.width // 2)  # Adjust the range and default value as needed
            text_y = st.slider('Y Coordinate', 0, img.height,
                               img.height // 2)  # Adjust the range and default value as needed

            if st.button('Add Text'):
                from PIL import ImageFont, ImageDraw  # Import ImageFont and ImageDraw here
                draw = ImageDraw.Draw(img)

                # Create a font with the selected size
                font = ImageFont.truetype("arial.ttf", text_size)  # You may need to specify the font file

                # Add the text to the image at the specified coordinates
                draw.text((text_x, text_y), text_to_add, fill='white', font=font)

                st.write("Image with Text")
                st.image(img, use_column_width=True, channels='RGB')
    if op == 'Image Corrections':

        img = st.file_uploader('Upload an image', type=['jpg', 'png', 'jpeg'])

        if img is not None:
            image = Image.open(img)
            st.sidebar.text('Original Image')
            st.sidebar.image(image, width=200)

        MImage = st.sidebar.radio('Image enhancement', ['Original', 'Contrast', 'brightness', 'Sharpness'])

        if MImage == 'Contrast':
            slide = st.sidebar.slider('Contrast', 0.0, 2.0, 1.0)
            enh = ImageEnhance.Contrast(image)
            contrast_image = enh.enhance(slide)
            st.image(contrast_image, width=Output_image)

        elif MImage == 'brightness':
            slide = st.sidebar.slider('brightness', 0.0, 5.0, 1.0)
            enh = ImageEnhance.Brightness(image)
            brightness_image = enh.enhance(slide)
            st.image(brightness_image, width=Output_image)

        elif MImage == 'Sharpness':
            slide = st.sidebar.slider('Sharpness', 0.0, 2.0, 1.0)
            enh = ImageEnhance.Sharpness(image)
            sharpness_image = enh.enhance(slide)
            st.image(sharpness_image, width=Output_image)
        else:
            st.image(image, width=Output_image)

    elif op == 'Information':
        st.subheader('Project by aditya,mayur,sachin,suraj')


if __name__ == '__main__':
    main()

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {

    visibility: hidden;

    }
footer:after {
    content:'made by acpceians'; 
    visibility: visible;
    display: block;
    position: relative;
    #background-color: red;
    padding: 5px;
    top: 2px;
}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)