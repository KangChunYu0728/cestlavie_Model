import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import io

def chart_analytics_ui(df):
    if df is None or df.empty:
        st.warning("⚠️ 沒有可分析的資料。")
        return

    # Chinese font settings
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False

    st.markdown("### 🕓 時間範圍篩選")
    min_date = df["種植日期"].min()
    max_date = df["採收日期"].max()

    col1, col2 = st.columns(2)
    with col1:
        start_year = st.selectbox("起始年份", list(range(min_date.year, max_date.year + 1)), index=0)
        start_month = st.selectbox("起始月份", list(range(1, 13)), index=0)
    with col2:
        end_year = st.selectbox("結束年份", list(range(start_year, max_date.year + 1)), index=max_date.year - start_year)
        end_month = st.selectbox("結束月份", list(range(1, 13)), index=11)

    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 28)

    filtered_df = df[(df["種植日期"] >= start_date) & (df["採收日期"] <= end_date)]

    if filtered_df.empty:
        st.warning("⚠️ 所選時間範圍內沒有資料")
        return

    chart_option = st.selectbox("請選擇要產生的圖表：", [
        "各產品平均種植時間",
        "各產品總數量統計",
        "不同狀態的產品分布",
        "自定義圖表"
    ])

    try:
        if chart_option == "不同狀態的產品分布":
            status_counts = filtered_df["狀態"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
            ax.set_title("🔄 不同狀態的產品分布")
            st.pyplot(fig)
            # export chart
            export_chart_as_image(fig)
        
        else:
            fig = plt.figure(figsize=(10, 5))
            if chart_option == "各產品平均種植時間":
                sns.barplot(data=filtered_df, x="產品名稱", y="種植時間（日）", estimator='mean', errorbar=None)
                plt.title("📈 各產品平均種植時間（日）")
            elif chart_option == "各產品總數量統計":
                counts = filtered_df["產品名稱"].value_counts()
                sns.barplot(x=counts.index, y=counts.values)
                plt.title("📊 各產品總數量統計")
                plt.xlabel("產品名稱")
                plt.ylabel("數量")
            elif chart_option == "自定義圖表":
                x_col = st.selectbox("選擇 X 軸欄位", options=filtered_df.columns)
                y_col = st.selectbox("選擇 Y 軸欄位", options=filtered_df.select_dtypes(include=['int64', 'float64']).columns)
                sns.barplot(data=filtered_df, x=x_col, y=y_col, estimator='mean', errorbar=None)
                plt.title(f"📊 {x_col} vs {y_col}")

            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
            # export chart
            export_chart_as_image(fig)

    except Exception as e:
        st.error(f"❌ 圖表錯誤: {str(e)}")
        

def export_chart_as_image(fig, filename="chart.png"):
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    st.download_button("📥 下載圖表 (PNG)", data=buf, file_name=filename, mime="image/png")
