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
        # 모델 로딩
        st.info("모델을 불러오는 중입니다. 약간의 시간이 걸릴 수 있어요...")
        summarizer = pipeline("summarization", model="digit82/kobart-summarization")
        sentiment_analyzer = pipeline("sentiment-analysis")
        st.success("모델 불러오기 완료!")

        # 기사 나누기
        articles = news_input.strip().split("\n\n")

        # 키워드 가중치
        keyword_weights = {
            "AI": 2, "인공지능": 2, "삼성": 3, "애플": 3,
            "오픈AI": 3, "전쟁": 4, "폭락": 4, "아이폰": 2, "코인": 2
        }

        scored = []
        for article in articles:
            score = 0
            score += sum([article.count(k) * w for k, w in keyword_weights.items()])
            if len(article) > 500:
                score += 2
            urgent_words = ["오늘", "긴급", "발표", "속보", "공식"]
            score += sum([2 for word in urgent_words if word in article])
            try:
                result = sentiment_analyzer(article[:512])[0]
                score += int(result["score"] * 5)
            except:
                pass
            scored.append((article, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_articles = scored[:3]

        # 점수 시각화
        st.subheader("📊 기사별 인기 예측 점수")
        titles = [art[:40].replace('\n', ' ') + "..." for art, _ in scored]
        scores = [score for _, score in scored]
        fig, ax = plt.subplots()
        ax.barh(titles, scores, color="skyblue")
        ax.set_xlabel("인기 예측 점수")
        ax.set_title("🔥 뉴스 인기 예측 점수")
        st.pyplot(fig)

        # 영상 스크립트 생성
        all_sections = "[인트로]\n오늘의 화제 뉴스 3가지, 지금부터 빠르게 알아보겠습니다.\n\n"
        for i, (article, _) in enumerate(top_articles):
            summary = summarizer(article[:1000])[0]['summary_text']
            easy_script = f"이 뉴스는 이런 내용이에요:\n\n{summary}\n\n쉽게 말하면, {summary[:50]} 같은 일이 벌어진 거예요!\n왜 중요하냐면, 앞으로 여기에 큰 변화가 생길 수도 있기 때문이에요."
            all_sections += f"[{i+1}. 뉴스 설명]\n{easy_script}\n\n"
        all_sections += "[마무리]\n오늘의 뉴스였습니다. 다음 영상에서 만나요!"

        st.subheader("📢 영상 스크립트 (전체)")
        st.text_area("스크립트", all_sections, height=500)