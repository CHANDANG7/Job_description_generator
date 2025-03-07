from flask import Flask, render_template, request, jsonify
import httpx
import json

# Initialize the Flask app
app = Flask(__name__)

# Configuration for open-webui API
WEBUI_ENABLED = True  # Set to use open-webui API
WEBUI_BASE_URL = "https://chat.ivislabs.in/api"
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key if needed
DEFAULT_MODEL = "gemma2:2b"  # Update to one of the available models

# Fallback to local Ollama API if needed
OLLAMA_ENABLED = True  # Set to False to use only the web UI API
OLLAMA_HOST = "localhost"
OLLAMA_PORT = "11434"
OLLAMA_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-job-description', methods=['POST'])
async def generate_job_description():
    # Get the form data from the request
    role_name = request.form['roleName']
    role_requirements = request.form['roleRequirements']
    company_values = request.form['companyValues']
    
    # Prepare the input prompt with explicit instructions for bullet points
    input_text = (
        f"Generate a **concise, structured job description** in **2-3 paragraphs** for the role below:\n\n"
        f"**Role:** {role_name}\n"
        f"**Company Values:** {company_values}\n\n"
        "Ensure the description is engaging and well-formatted. Include:\n"
        "- An introduction with a brief role overview.\n"
        "- **Key Responsibilities** in bullet points.\n"
        "- **Requirements** in bullet points.\n"
        "- **Benefits** in bullet points.\n\n"
        "Make the job description clear, professional, and appealing."
    )
    
    # Try using the open-webui API first if enabled
    if WEBUI_ENABLED:
        try:
            # Prepare the payload for the Open-webui API
            messages = [{"role": "user", "content": input_text}]
            request_payload = {
                "model": DEFAULT_MODEL,
                "messages": messages
            }
            
            # Call the Open-webui API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{WEBUI_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=request_payload,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = ""

                    if "choices" in result and len(result["choices"]) > 0:
                        choice = result["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            generated_text = choice["message"]["content"]
                    
                    return jsonify({'jobDescription': generated_text.strip()})
                else:
                    raise Exception("Failed to generate content from Open-webui API")
        
        except Exception as e:
            print(f"Error with Open-webui API: {str(e)}")
    
    # Fallback to direct Ollama API if Open-webui failed and Ollama is enabled
    if OLLAMA_ENABLED:
        print("Falling back to direct Ollama API")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_API_URL}/generate",
                json={
                    "model": DEFAULT_MODEL,
                    "prompt": input_text,
                    "stream": False
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                return jsonify({'jobDescription': generated_text})
            else:
                return jsonify({'error': "Failed to generate content from Ollama API"})

    return jsonify({'error': "Failed to generate content from any available LLM API"})

if __name__ == '__main__':
    app.run(debug=True)
