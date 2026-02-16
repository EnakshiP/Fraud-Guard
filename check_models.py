import google.generativeai as genai

genai.configure(api_key="AIzaSyACeLVqD9zhlIH554Za7DsMYFg6o-r-q7c")

print("Listing available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)