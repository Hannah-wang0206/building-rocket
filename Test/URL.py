import streamlit as st
import requests

# Streamlit app
st.title("Image Upload with Public URL Generation")
st.header("Upload an image to get a public URL")

# Upload section
uploaded_image = st.file_uploader("Choose an image to upload", type=["png", "jpg", "jpeg"])

# Flask server configuration
FLASK_SERVER_URL = "http://14.136.11.131:5000"  # 替换 <your_public_ip> 为实际的公网 IP

if uploaded_image is not None:
    if st.button("Generate Public URL"):
        try:
            # Send the uploaded file to Flask server
            files = {"file": (uploaded_image.name, uploaded_image, uploaded_image.type)}
            response = requests.post(FLASK_SERVER_URL, files=files)

            if response.status_code == 200:
                public_url = response.json()["url"]
                st.success("Public URL generated successfully!")
                st.write(public_url)
                st.image(public_url, caption="Uploaded Image", use_column_width=True)
            else:
                st.error(f"Failed to upload image. Error: {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
