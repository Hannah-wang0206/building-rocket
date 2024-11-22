import streamlit as st
import replicate
from PIL import Image
import requests
from io import BytesIO

# 在此设置您的 Replicate API Token
replicate_client = replicate.Client(api_token="r8_MeFEKgscN4NYt96L0Z4awdKSCFeEw4d3fUO")

# 然后使用该客户端进行 API 调用
st.title("AI Image Generation with Replicate")

# Input section
st.header("Input")
image_url = st.text_input("Enter the URL of a public image:", "https://example.com/image.png")
prompt = st.text_input("Enter a description (prompt):", "a photo of a brightly colored turtle")

if st.button("Generate"):
    if image_url and prompt:
        try:
            input_data = {
                "image": image_url,
                "prompt": prompt,
            }

            # Call Replicate API with authenticated client
            st.write("Generating images...")
            output = replicate_client.run(
                "jagilley/controlnet-scribble:435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117",
                input=input_data,
            )

            # Display outputs
            st.header("Generated Outputs")
            for index, item in enumerate(output):
                image_response = requests.get(item)  # Fetch generated image
                output_image = Image.open(BytesIO(image_response.content))
                st.image(output_image, caption=f"Output Image {index + 1}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid image URL and prompt.")
