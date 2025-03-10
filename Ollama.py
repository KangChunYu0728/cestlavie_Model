import subprocess

def check_ollama_installed():
    try:
        subprocess.run(["ollama", "--version"], check=True)
        print("✅ Ollama is installed.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ollama not installed. Please install it from https://ollama.com/download")
        return False

def pull_model(model_name="mistral"):
    try:
        result = subprocess.run(["ollama", "pull", model_name], check=True, capture_output=True, text=True)
        print(f"✅ Model '{model_name}' downloaded successfully!")
        print("🔍 Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download model '{model_name}'.")
        print("Error:", e.stderr)

if check_ollama_installed():
    pull_model("mistral")
