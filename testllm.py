import google.generativeai as genai

genai.configure(api_key="AIzaSyCcJH6gMnE9scKHSTKfGafCzYErNKuHx9I")
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Say hello world")
print(response.text)