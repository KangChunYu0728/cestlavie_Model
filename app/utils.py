import pandas as pd
import json
import numpy as np  # 需要這個來判斷 NaN
from tkinter import filedialog, Tk
import os
from deep_translator import GoogleTranslator  # pip install deep-translator
import re
from sentence_transformers import SentenceTransformer
import faiss
import pickle

# 所有產品名稱（來自你圖片）
product_list = [
    "奶油波士頓", "奶波", "玉芙蓉", "冰花", "貝比萵", "紅火焰", "紅奶油",
    "紅狐", "紅彤", "紅橙", "紅甜脆", "紅芽心", "紅綠",
    "英貝比萵", "英貝比萵(不分品種)", "恐龍甘藍", "恐龍羽衣甘藍", "粉嫩天使",
    "捲葉甘藍", "捲葉羽衣甘藍", "菊苣", "試種", "綠水晶", "綠火焰",
    "綠狐", "綠甜脆", "綠橡","綠蘿蔓","綠寶石"
]

question_list = [ "產品名稱","產品編號", "種植日期", "採收日期", "狀態","多少顆","多少斤","多少公斤",
                 "多少公克","多少片","多少株","多少棵","多少株數","多少片數","多少斤數","多少公斤數","多少公克數",
                 "最多","最少","平均","中位數","標準差","變異數","最大值","最小值",
                 "總和","總計","總數","總量","總重量","總斤數","總公斤數","總公克數",
                 "價格","單價","售價"
]


# 讀取 JSON 檔案（手動選擇）
def select_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="選擇 JSON 檔案",
        filetypes=[("JSON files", "*.json")]
    )
    return file_path




#讀取 JSON 並過濾欄位齊全、無空值的資料
def load_data(file_path):
    """讀取 JSON 並過濾欄位齊全、無空值的資料"""
    try:
        print(f"📂 正在讀取檔案: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        required_columns = ["產品編號", "產品名稱", "種植日期", "採收日期", "狀態"]
        if "Sheet1" not in json_data:
            raise ValueError("❌ JSON 格式錯誤: 找不到 'Sheet1'")

        valid_records = []
        invalid_count = 0

        for record in json_data["Sheet1"]:
            # 確保欄位都存在
            if all(col in record for col in required_columns):
                # 確保欄位內容不是 None、空字串或 NaN
                if all(
                    record[col] not in [None, ""] and not pd.isna(record[col])
                    for col in required_columns
                ):
                    valid_records.append(record)
                else:
                    invalid_count += 1
            else:
                invalid_count += 1

        if not valid_records:
            raise ValueError("❌ 沒有符合要求的資料記錄")

        print(f"✅ 成功載入 {len(valid_records)} 筆有效資料")
        if invalid_count > 0:
            print(f"⚠️ 排除 {invalid_count} 筆含空值或不完整的資料")

        # 轉成 DataFrame
        df = pd.DataFrame(valid_records)
        df["種植日期"] = pd.to_datetime(df["種植日期"])
        df["採收日期"] = pd.to_datetime(df["採收日期"])
        df["種植時間（日）"] = (df["採收日期"] - df["種植日期"]).dt.days

        return df

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return None
    

#翻譯
def contains_english(text):
    """檢查是否包含英文"""
    return re.search(r'[a-zA-Z]', text) is not None

def translate_to_chinese(text):
    """翻譯英文 → 中文"""
    try:
        return GoogleTranslator(source='auto', target='zh-TW').translate(text)
    except Exception as e:
        print(f"⚠️ 翻譯失敗：{str(e)}")
        return text  # 回傳原文


def df_to_documents(df):
    documents = []
    for _, row in df.iterrows():
        doc = f"產品編號為 {row['產品編號']}，名稱是 {row['產品名稱']}，種植日期是 {row['種植日期']}，採收日期是 {row['採收日期']}，狀態為 {row['狀態']}，種植時間是 {row['種植時間']}。"
        documents.append(doc)
    return documents

import pickle

def build_faiss_index(documents, index_path="faiss_index.index", doc_path="documents.pkl"):
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = model.encode(documents)
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # 儲存 index 到檔案
    faiss.write_index(index, index_path)

    # 修正這裡 ↓↓↓↓↓
    with open(doc_path, "wb") as f:
        pickle.dump({
            "documents": documents,
            "model_name": model._first_module().auto_model.config._name_or_path  # ← 修正點
        }, f)

    print(f"✅ FAISS Index 與文件儲存完成，共 {index.ntotal} 筆。")
    return index, documents, model



def search_similar_documents(question, index, documents, model, top_k=5):
    """查詢與問題最相關的文件段落"""
    query_embedding = model.encode([question])
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(documents):
            results.append(documents[idx])
    return results


def load_faiss_index(index_path="faiss_index.index", doc_path="documents.pkl"):
    if not os.path.exists(index_path) or not os.path.exists(doc_path):
        return None, None, None

    # 載入 index
    index = faiss.read_index(index_path)

    # 載入 documents 和模型
    with open(doc_path, "rb") as f:
        data = pickle.load(f)
        documents = data["documents"]
        model = SentenceTransformer(data["model_name"])

    print(f"📦 已從檔案載入 FAISS Index，共 {index.ntotal} 筆。")
    return index, documents, model

