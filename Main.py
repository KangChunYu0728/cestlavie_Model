import pandas as pd # type: ignore
import subprocess
import ollama # type: ignore

### Choose and Set UP Ollama Model
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
        print(f"📦 Pulling model '{model_name}' from Ollama...")
        # Stream output to terminal in real-time
        process = subprocess.Popen(["ollama", "pull", model_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line.strip())
        process.wait()
        if process.returncode == 0:
            print(f"✅ Model '{model_name}' downloaded successfully!")
        else:
            print("❌ Model pull failed.")
    except Exception as e:
        print("Error:", e)

# Run
if check_ollama_installed():
    pull_model("mistral")


#### Read the Input Production information
df = pd.read_excel("merged_product_data_sorted.xlsx")
# Show data summary
print("Loaded Excel data. Here's a preview:")
print(df.head())

# Let user type their own prompt in the terminal
user_input = input("\n Typer your analysis reuquest for the AI:")

# Prepare prompt message
prompt = f"{user_input}\n\nHere is the salad product data:\n{df.to_string(index=False)}"

#Chat with Ollama Model
response = ollama.chat(
    model='mistral',
    messages=[{'role': 'user', 'content': prompt}]
)

# Print the response from the model
print("💬 Response from Ollama:")
print(response['message']['content'])


