import requests
import os 

#os.environ["hf_api_key"] = {hf_api_key}

from fastapi import FastAPI

app = FastAPI()

class HuggingFaceAPI:
    def __init__(self, token):
        self.token = token

    def send_request(self, url, method, body):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=body)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    def text_translation(self, text, target_language):
        source_language = self.language_detection(text) 
        url = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-"+source_language+"-"+target_language
        method = "POST"
        body = {
            "inputs": text
        }
        return self.send_request(url, method, body)


    def text_translation(self, text, source_language, target_language):
      #return ""
        url = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-"+source_language+"-"+target_language
        method = "POST"
        body = {
            "inputs": text
        }
        return self.send_request(url, method, body)

    def language_detection(self, text):
        url = "https://api-inference.huggingface.co/models/papluca/xlm-roberta-base-language-detection"
        method = "POST"
        body = {
            "inputs": text
        }
        return self.send_request(url, method, body)

# ... existing API endpoints ...

@app.post("/hf-inference/language_detection")
async def language_detection_api(text: str):
    language_detection_response = api.language_detection(text)
    return language_detection_response

@app.post("/hf-inference/text_translation")
async def text_translation_api(text: str, source_language:str, target_language: str):
    text_translation_response = api.text_translation(text, source_language, target_language)
    return text_translation_response

@app.post("/hf-inference/text_translation")
async def text_translation_api(text: str, target_language: str):
    text_translation_response = api.text_translation(text, target_language)
    return text_translation_response

### ENd of Fast API endpoints

api = HuggingFaceAPI( os.environ.get("hf_api_key") )

# Define the function to be called when inputs are provided
def hf_inference_translate(prompt="Wie kann ich Ihnen helfen?",  target_language="en"):
    print(prompt)
    # Call the respective API methods 
    # Get the input language
    chat_response_languagedetected = ""
    chat_response_languagedetected = api.language_detection(prompt)
    print(chat_response_languagedetected[0][0]['label'])
    # Translate based on input prompt, detected language and chosen target language
    text_translation_response = api.text_translation(prompt, chat_response_languagedetected[0][0]['label'], target_language) 
    print(text_translation_response) 
    # Extract the labels and scores from the result
    label_scores = {entry['label']: entry['score'] for entry in chat_response_languagedetected[0][:3]}
    print(label_scores)
    # Return the API responses #
    return  text_translation_response[0]['translation_text'],label_scores

text = "Hallo, ich bin Christof. Wie geht es dir?"
#text = "Меня зовут Вольфганг и я живу в Берлине"
translation_response = hf_inference_translate(text, "en")
print(translation_response)



import gradio as gr
import requests
 

iface = gr.Interface(
    fn=hf_inference_translate,
    inputs=[
        gr.inputs.Textbox(label="Input", lines=5, placeholder="Enter text to translate"),
        gr.inputs.Dropdown(["en", "fr", "de", "es", "ru"], default="de", label="Select target language")
    ],
    outputs=[
        gr.outputs.Textbox(label="Translated text"),
        gr.outputs.Label(label="Detected languages", num_top_classes=3)
    ],
    title="🧐 Translation Interface",
    description="Type something in any language below and then click Run to see the output in the chosen target language.",
    examples=[["Wie geht es Dir?", "fr"], ["Do you need help?", "de"], ["J'ai besoin d'aide ?", "en"]],
    article="## Text Examples",
    article_description="Use examples",
    #live=True,
    debug=True,
    cache_examples=True
)

 

# Create a Gradio interface
#queue
iface.queue(concurrency_count=3)
# Run the Gradio interface
#iface.launch(share=True)
iface.launch(debug=True)
 


