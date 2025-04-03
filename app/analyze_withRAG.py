import pandas as pd
import ollama
import json
import time
from difflib import SequenceMatcher
from utils import load_data,product_list,select_file,question_list,contains_english,translate_to_chinese,df_to_documents,build_faiss_index,search_similar_documents 
from tkinter import filedialog, Tk
import os
from sentence_transformers import SentenceTransformer
from utils import load_faiss_index



# 初始化 Ollama 客戶端
client = ollama.Client()

# 全域變數存放資料
json_file_path = None
df = None
summary = None
documents = None
# 建立模型
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

output_dir = "test_results"
def load_example_log():
    """讀取過去範例紀錄，轉為 few-shot 語料"""
    log_path = os.path.join("test_results", "test_results.csv")
    if not os.path.exists(log_path):
        return ""

    df_log = pd.read_csv(log_path)

    examples = df_log.head(10)  # 取前10筆範例

    example_text = ""
    for i, row in examples.iterrows():
        example_text += f"""
        【範例 {i+1}】
        問題：{row['Question']}
        答案：{row['Expected Answer']}
        錯誤回答：{row['Generated Answer']}

"""
    return example_text


def similarity(generated_answer, expected_answer):
    """
    根據預期答案中有多少字被回應正確命中，決定相似度。
    - 完全包含 ➜ 1.0
    - 對到部分 ➜ 0.3 ~ 0.9（依字元命中比例）
    - 完全沒對到 ➜ 0.0
    """
    matched_chars = sum(1 for c in expected_answer if c in generated_answer)
    total_chars = len(expected_answer)
    if total_chars == 0:
        return 0.0  # 避免除以零的錯誤
    return matched_chars / total_chars


def load_json():
    global json_file_path, df, summary
    file_path = select_file()
    if file_path:
        df = load_data(file_path)
        if df is not None:
            global documents, index2, docs, embedding_model
            json_file_path = file_path
            summary = df.describe(include='all').to_string()
            print("✅ 資料摘要已生成！")
            documents = df_to_documents(df)
           
            #如果第一次執行 則注解這一行
            index2, docs, embedding_model = load_faiss_index()

            # 如果第一次執行 則取消注解這一行
            # index2, docs, embedding_model = build_faiss_index(documents)
            print("✅ FAISS 向量索引已建立！")


        else:
            print("❌ 資料加載失敗！")
            exit()
    else:
        print("⚠️ 未選擇檔案，程式結束。")
        exit()







def filter_df_by_question(df, question, product_list): #產品關鍵字提取
    for name in product_list:
        if name in question:
            filtered = df[df["產品名稱"].str.contains(name, na=False)]
            print(f"偵測到產品名稱：{name}，共 {len(filtered)} 筆")
            print(filtered.head(0).to_string(index=False))  # 列印出篩選結果
            return filtered, name

    return df.head(10000), None  

def extract_keyword(question): #問題關鍵字提取
    for name in question_list:
        if name in question:
            print(f"偵測到問題關鍵字：{name}")
            return name
    return None



def generate_prompts(question):
    filtered_df, matched_name = filter_df_by_question(df, question, product_list)
    table_text = filtered_df.to_markdown(index=False)
    matched_question = extract_keyword(question)
    
    #查詢過去範例紀錄
    example_text = load_example_log()

    # 查詢最相關的文件段落
    top_k_docs = search_similar_documents(question, index2, docs, embedding_model, top_k=5)
    print(f"🔢 擷取段落數量：{len(top_k_docs)}")

    # 將結果合併成一段文字
    retrieved_context = "\n".join(top_k_docs)

    print("🔍 擷取到的相關資料片段：")
    print(retrieved_context)

    system_prompt = f"""
    你是一位資料統計助理，請根據表格中的資料回答使用者的問題。請嚴格遵守以下規則：

    - Follow the data，you are not allowed to predict or guess.
    - Your answer must be in traditional Chinese.
    - Every row in the data represents a product.
    - If there aren't any relative information in the data,please answer：「No information」。
    - It is forbidden to give the answer which is not in the data, and not to repeat the question.
    - Here are some examples of the questions , correct answers and wrong answers,please avoid answering like the wrong answers:
{example_text}
"""

    user_prompt = f"""
        Please answer the question ：
        question：{question}
        here is the data summary：
        {summary}
       
        here is the data：
        {retrieved_context}
"""

    return system_prompt, user_prompt


def generate_answer(system_prompt, user_prompt):
    try:
        response = client.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=True
        )
        raw = ''.join([chunk["message"]["content"] for chunk in response])
        
        # 如果包含英文，自動翻譯
        if contains_english(raw):
            print("🌐 偵測到英文，自動翻譯中...")
            translated = translate_to_chinese(raw)
            return translated
        return raw
    except Exception as e:
        return f"❌ 回應錯誤: {str(e)}"



def run_test_with_prompts(question, expected_answer):
    system_prompt, user_prompt = generate_prompts(question)
    start_time = time.time()
    response = generate_answer(system_prompt, user_prompt)
    end_time = time.time()

    acc = similarity(response, expected_answer)
    duration = end_time - start_time

    print(f"🔍 測試問題：{question}")
    print(f"📝 回應：{response}")
    print(f"🎯 相似度：{acc:.2f}")
    print(f"⏳ 耗時：{duration:.2f} 秒")
    print("=" * 80)

    return {
        "Question": question,
        "Expected Answer": expected_answer,
        "Generated Answer": response,
        "Accuracy": acc,
        "Duration": duration,
        "Pass": acc >= 0.8
    }

if __name__ == "__main__":
    load_json()

    test_cases = {
        "紅奶油共有多少顆？": "3659顆",
        "紅火焰共有多少顆？": "5105顆",
        "紅火焰的價格是多少？": "從資料中無法得知價格，因爲無此欄位",
        "產品編號為1101是哪個產品？": "產品編號為1101的產品包含紅火焰，紅狐，奶波，綠捲等產品",
        "產品編號為1102是哪個產品？": "產品編號為1102的產品包含紅火焰，紅狐，奶波，綠捲等產品",
        "統計最多的產品是哪兩種？": "紅火焰，綠橡",
        "統計最少的產品是哪兩種？": "奶油波士頓，紅蔓心",
        "大部分的產品狀態是什麽":"大部分的產品狀態是種植中",
        "產品的種植時間分佈？" :"產品的種植時間分佈在 40 到 70天之間，大部分在42天左右",
        "最早統計的資料的是哪一筆" :"最早統計的資料是 2022-03-03",
        "最晚統計的資料的是哪一筆" :"最晚統計的資料是 2025-03-24",
        "產品編號為1101的產品狀態是什麽？":"產品編號為1101的產品狀態是種植中",
        "綠橡的產品編號是多少？":"綠橡的產品編號從5160到8126都有分佈"


    }

    results = []
    for question, expected in test_cases.items():
        results.append(run_test_with_prompts(question, expected))

    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_results.csv")
    pd.DataFrame(results).to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False, encoding="utf-8-sig")
    print(f"✅ 測試完成，結果已儲存至：{output_path}")
