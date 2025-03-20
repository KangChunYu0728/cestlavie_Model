import pandas as pd 
import subprocess
import ollama 
import matplotlib.pyplot as plt
import seaborn as sns 
import os

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

# Run Setup
if check_ollama_installed():
    pull_model("mistral")


#### Read the Input Production information
df = pd.read_excel("/Users/davidkang/Desktop/Cest la Vie/cestlavie_Model/cestlavie_Model/app/merged_product_data_sorted.xlsx")
df["種植日期"] = pd.to_datetime(df["種植日期"])
df["採收日期"] = pd.to_datetime(df["採收日期"])

# Calculate new column for the planting period
df["種植時間（日）"] = (df["採收日期"] - df["種植日期"]).dt.days


# Show data summary
print("Loaded Excel data. Here's a preview:")
print(df.head())

### Let user type their own prompt in the terminal
user_input = input("\n Typer your analysis reuquest for the AI:")

### Generate Summary Text for analysis
summary = df.describe(include='all').to_string()
prompt = f"{user_input}\n\Here is the summarized salad product data:\n{summary}"

#Chat with Ollama Model
response = ollama.chat(
    model='mistral',
    messages=[{'role': 'user', 'content': prompt}]
)

# Print the response from the model
print("💬 Response from Ollama:")
print(response['message']['content'])


### 7️⃣ Create Visualization
# Bar plot: average planting duration per product
plt.figure(figsize=(10, 5))
sns.barplot(data=df, x="產品名稱", y="種植時間（日）", estimator='mean', errorbar=None)
plt.title("📈 各產品平均種植時間（日）")
plt.xticks(rotation=45)
#plt.tight_layout()

# Save the chart
#output_file = "salad_growth_chart.png"
#plt.savefig(output_file)
#print(f"\n📁 Chart saved as: {output_file}")