import streamlit as st
import cv2
import numpy as np
import base64
from PIL import Image
import io


# 假设你的LoRA模型已经被加载
# 这里使用一个占位函数来模拟模型的预测
def lora_model_predict(image):
    # 这里应该是你的LoRA模型的预测代码
    # 例如：return model.predict(image)
    return Image.fromarray(np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8))


def main():
    st.title('火箭造型图片生成器')

    uploaded_file = st.file_uploader("上传你的手绘线稿", accept_multiple_files=False)

    if uploaded_file is not None:
        # 将上传的文件转换为OpenCV图像格式
        image = np.asarray(Image.open(uploaded_file))

        # 显示原始图片
        st.image(image.tobytes(), caption='原始图片', use_column_width=True)

        # Canny边缘检测
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)

        # 显示边缘检测后的图片
        st.image(edges, caption='Canny边缘检测结果', use_column_width=True)

        # 使用LoRA模型生成火箭照片
        generated_image = lora_model_predict(edges)

        # 显示生成的火箭照片
        st.image(generated_image, caption='生成的火箭照片', use_column_width=True)


if __name__ == '__main__':
    main()