import streamlit as st
from transformers import pipeline
import matplotlib.pyplot as plt
import matplotlib

# ✅ 한글 깨짐 방지
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

st.title("🔥 뉴스 스크립트 자동 생성기")

# 사용자 입력
news_input = st.text_area("📰 뉴스 기사 4~5개를 붙여넣어 주세요 (빈 줄로 구분)", height=300)

# 실행 버튼
if st.button("생성 시작"):
    with st.spinner("분석 중..."):

        # 기사 나누기
        articles = news_input.strip().split("\n\n")

        # 요약기 및 감정 분석기 준비
        summarizer = pipeline("summarization", model="digit82/kobart-summarization")
        sentiment_analyzer = pipeline("sentiment-analysis")  # 영어 모델이지만 테스트용 사용

        # 키워드 가중치
        keyword_weights = {
            "AI": 2, "인공지능": 2, "삼성": 3, "애플": 3,
            "오픈AI": 3, "전쟁": 4, "폭락": 4, "아이폰": 2, "코인": 2
        }

        scored = []
        for article in articles:
            score = 0

            # 🔑 키워드 점수
            score += sum([article.count(k) * w for k, w in keyword_weights.items()])

            # 📏 길이 점수
            if len(article) > 500:
                score += 2

            # ⏱ 시급성 키워드
            urgent_words = ["오늘", "긴급", "발표", "속보", "공식"]
            score += sum([2 for word in urgent_words if word in article])

            # 😡 감정 분석 점수 (영문만 정확, 한국어는 참고용)
            try:
                result = sentiment_analyzer(article[:512])[0]
                score += int(result["score"] * 5)
            except:
                pass

            scored.append((article, score))

        # 상위 3개 기사 선택
        scored.sort(key=lambda x: x[1], reverse=True)
        top_articles = scored[:3]

        # 📊 시각화
        st.subheader("📊 기사별 인기 예측 점수")
        titles = [art[:40].replace('\n', ' ') + "..." for art, _ in scored]
        scores = [score for _, score in scored]
        fig, ax = plt.subplots()
        ax.barh(titles, scores, color="skyblue")
        ax.set_xlabel("인기 예측 점수")
        ax.set_title("🔥 뉴스 인기 예측 점수")
        st.pyplot(fig)

        # 🎬 영상 스크립트 생성
        all_sections = "[인트로]\n오늘의 화제 뉴스 3가지, 지금부터 빠르게 알아보겠습니다.\n\n"
        for i, (article, _) in enumerate(top_articles):
            summary = summarizer(article[:1000])[0]['summary_text']
            all_sections += f"[{i+1}. 뉴스 요약]\n{summary}\n\n"
        all_sections += "[마무리]\n오늘의 뉴스였습니다. 다음 영상에서 만나요!"

        st.subheader("📢 영상 스크립트 (전체)")
        st.text_area("스크립트", all_sections, height=500)
