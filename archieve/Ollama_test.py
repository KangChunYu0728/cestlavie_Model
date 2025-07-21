import ollama

test_cases = [
    {"prompt": "哪一個產品平均種植時間最長？", "expected": "紅火焰"},  # partial match ok
    {"prompt": "請找出有異常值的產品", "expected": "異常值"},
]

model = "mistral"

for i, test in enumerate(test_cases, 1):
    print(f"\n🔍 Test {i}: {test['prompt']}")
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": test['prompt']}]
    )
    answer = response['message']['content']
    print("📤 AI 回答:", answer)
    if test["expected"] in answer:
        print("✅ 測試通過")
    else:
        print("❌ 測試未通過")
