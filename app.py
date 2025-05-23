import streamlit as st
from transformers import pipeline
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib

# ✅ 한글 깨짐 방지 (Streamlit Cloud 호환 폰트)
matplotlib.rcParams['font.family'] = 'NanumGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

st.title("🔥 뉴스 스크립트 자동 생성기 (경량 버전)")

news_input = st.text_area("📰 뉴스 기사 2~3개를 붙여넣어 주세요 (빈 줄로 구분)", height=300)

if st.button("생성 시작"):
    with st.spinner("AI 요약 중..."):
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        articles = news_input.strip().split("\n\n")

        keyword_weights = {
            "AI": 2, "OpenAI": 3, "Samsung": 3, "Apple": 3,
            "Google": 2, "ChatGPT": 3, "robot": 2, "war": 4, "crisis": 4
        }

        scored = []
        for article in articles:
            score = 0
            score += sum([article.count(k) * w for k, w in keyword_weights.items()])
            if len(article) > 500:
                score += 2
            scored.append((article, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_articles = scored[:3]

        st.subheader("📊 기사별 인기 예측 점수")
        titles = [art[:40].replace('\n', ' ') + "..." for art, _ in scored]
        scores = [score for _, score in scored]
        fig, ax = plt.subplots()
        ax.barh(titles, scores, color="skyblue")
        ax.set_xlabel("인기 예측 점수")
        ax.set_title("🔥 뉴스 인기 예측 점수")
        st.pyplot(fig)

        all_sections = "[인트로]\n오늘의 화제 뉴스 3가지, 지금부터 빠르게 알아보겠습니다.\n\n"
        for i, (article, _) in enumerate(top_articles):
            summary = summarizer(article[:1000])[0]['summary_text']
            easy_script = f"이 뉴스는 이런 내용이에요:\n\n{summary}\n\n쉽게 말하면, {summary[:50]} 같은 일이 벌어진 거예요!"
            all_sections += f"[{i+1}. 뉴스 설명]\n{easy_script}\n\n"
        all_sections += "[마무리]\n오늘의 뉴스였습니다. 다음 영상에서 만나요!"

        st.subheader("📢 영상 스크립트 (전체)")
        st.text_area("스크립트", all_sections, height=500)