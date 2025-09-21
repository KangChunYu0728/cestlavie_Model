import pandas as pd
import os
import json
import streamlit as st

@st.cache_data
def load_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "../Data/merged_product_data_sorted_json.json")

        if not os.path.exists(file_path):
            st.error(f"❌ 找不到檔案: {file_path}")
            return None

        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        required_columns = ["產品編號", "產品名稱", "種植日期", "採收日期", "狀態"]
        if 'Sheet1' not in json_data:
            st.error("❌ JSON 格式錯誤：找不到 'Sheet1' 欄位")
            return None

        valid_records = [record for record in json_data['Sheet1']
                         if all(col in record for col in required_columns)]

        if not valid_records:
            st.error("❌ 沒有符合要求的資料記錄")
            return None

        df = pd.DataFrame(valid_records)
        df["種植日期"] = pd.to_datetime(df["種植日期"])
        df["採收日期"] = pd.to_datetime(df["採收日期"])
        df["種植時間（日）"] = (df["採收日期"] - df["種植日期"]).dt.days

        return df

    except Exception as e:
        st.error(f"❌ 載入資料時發生錯誤: {str(e)}")
        return None
