import streamlit as st
import requests
import replicate
from PIL import Image
from io import BytesIO

# 初始化 Replicate 客户端
replicate_client = replicate.Client(api_token="r8_MeFEKgscN4NYt96L0Z4awdKSCFeEw4d3fUO")

# Streamlit 页面标题
st.title("AI Image Generation with Replicate")

# 上传图片
uploaded_image = st.file_uploader("Upload an image file:", type=["png", "jpg", "jpeg"])
prompt = st.text_input("Enter a description (prompt):", "a photo of a real rocket")

if st.button("Generate"):
    if uploaded_image and prompt:
        try:
            # 将上传文件保存到临时文件
            temp_file_path = "./temp_uploaded_image.png"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_image.read())

            # 打开文件对象并传递给 Replicate API
            with open(temp_file_path, "rb") as image_file:
                input_data = {
                    "image": image_file,
                    "prompt": prompt,
                }
                st.write("Generating images...")
                output = replicate_client.run(
                    "jagilley/controlnet-scribble:435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117",
                    input=input_data,
                )

            # 显示生成的图片并保存到本地
            st.header("Generated Outputs")
            for index, item in enumerate(output):
                image_response = requests.get(item)  # 获取生成的图片
                output_image = Image.open(BytesIO(image_response.content))

                # 显示在 Streamlit 页面上
                st.image(output_image, caption=f"Output Image {index + 1}")

                # 保存到本地
                with open(f"output_{index}.png", "wb") as file:
                    file.write(image_response.content)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload an image and enter a prompt.")
