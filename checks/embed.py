import os
from google import genai
from dotenv import load_dotenv

load_dotenv()



client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Danh sách các mô hình hỗ trợ Embedding:\n")

for model in client.models.list():
    # Kiểm tra mô hình có hỗ trợ phương thức embed_content không
    if "embedContent" in model.supported_actions:
        print(f"📌 Tên định danh (Name): {model.name}")
        print(f"   Tên hiển thị:         {model.display_name}")
        print(f"   Mô tả:                {model.description}")
        print("-" * 60)