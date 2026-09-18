import google.generativeai as genai

genai.configure(api_key="AQ.Ab8RN6KEi7SflvblaBDkIpX5NhlbjIub65Br1oxd6CsiboA2BA")

print("Các mô hình hỗ trợ generateContent mà bạn có thể dùng:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)