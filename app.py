import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="한화시스템 방산 관리회계 분석", page_icon="📊", layout="wide")

# -----------------------------
# 기본 스타일
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
div[data-testid="stMetric"] {background:#f7f7f8; border:1px solid #e6e6e8; padding:14px; border-radius:12px;}
.small-note {color:#666; font-size:0.88rem;}
.insight {background:#f6f7fb; border-left:4px solid #555; padding:14px 16px; border-radius:8px; margin:8px 0;}
.risk {background:#fff7f2; border-left:4px solid #d66b2c; padding:14px 16px; border-radius:8px; margin:8px 0;}
.good {background:#f3f8f4; border-left:4px solid #4c8a5b; padding:14px 16px; border-radius:8px; margin:8px 0;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 1. 방산 분기 손익: 회사 실적발표 자료
# 단위: 억원
# -----------------------------
quarterly = pd.DataFrame([
    ["2023Q1", 2924, 133, 4.5, "철매-II 성능개량 사업 종료 등으로 매출 감소"],
    ["2023Q2", 4481, 282, 6.3, "군위성통신체계-II·TICN 4차 양산 매출 증가, 위성 자체투자 부담"],
    ["2023Q3", 4594, 338, 7.4, "TICN 4차 양산·30mm 차륜형대공포 양산 매출 증가"],
    ["2023Q4", 6171, 232, 3.8, "TICN 4차 양산·수출사업 반영, 분기 수익성 둔화"],
    ["2024Q1", 3817, 340, 8.9, "TICN 4차 양산·수출 매출 반영"],
    ["2024Q2", 4932, 609, 12.3, "폴란드 K2·TICN 4차 양산, 수출 비중 증가·원가절감"],
    ["2024Q3", 4678, 463, 9.9, "폴란드 K2·TICN 4차 양산, 수출 비중 증가"],
    ["2024Q4", 7561, 278, 3.7, "폴란드 K2·중동 MSAM MFR·TMMR 2차 양산, 자체투자 개발비·판관비 증가"],
    ["2025Q1", 4303, 503, 11.7, "중동 MSAM MFR·폴란드 K2 1차 수출"],
    ["2025Q2", 4702, 525, 11.2, "TICN 4차 양산 종료 영향"],
    ["2025Q3", 4814, 498, 10.3, "위성·TICN TMMR 2차 양산·UAE MSAM MFR"],
    ["2025Q4",10569, 765, 7.2, "폴란드 K2·UAE/사우디 MSAM MFR·위성·TMMR 2차 양산"],
    ["2026Q1", 4712, 690,14.6, "UAE·사우디 MSAM MFR, KF-21 AESA·항전장비 등"],
    ["2026Q2", 7006,1037,14.8, "폴란드 K2·UAE/사우디 MSAM MFR, 울산급 Batch-III, KF-21 AESA·항전장비"],
], columns=["분기","방산매출","방산영업이익","영업이익률","회사제시_주요원인"])

quarterly["매출_YoY"] = quarterly["방산매출"].pct_change(4) * 100
quarterly["영업이익_YoY"] = quarterly["방산영업이익"].pct_change(4) * 100
quarterly["OPM_변화_YoY"] = quarterly["영업이익률"].diff(4)
quarterly["매출_QoQ"] = quarterly["방산매출"].pct_change() * 100
quarterly["영업이익_QoQ"] = quarterly["방산영업이익"].pct_change() * 100

# -----------------------------
# 2. 생산능력/실적
# 사업보고서·반기보고서에서 확인된 방산 구미사업장
# 단위: 억원
# -----------------------------
production = pd.DataFrame([
    ["2023 FY", 11662.48, 10600.56, 90.89],
    ["2024 FY", 12896.84, 11012.33, 85.39],
    ["2025 H1", 7402.64, 6230.43, 84.16],
    ["2025 FY", 17294.00, 14478.00, 83.72],
    ["2026 H1", 8696.00, 8086.00, 92.99],
], columns=["기간","생산능력","생산실적","가동률"])

# -----------------------------
# 3. 프로젝트 예시 데이터
# 공시된 주요 방산 프로젝트 구조를 재현.
# 사용자가 원하면 추후 전체 프로젝트를 분기별로 확장 가능.
# -----------------------------
projects = pd.DataFrame([
    ["Project A","장기 방산 프로젝트",22.44,1219.60,170.55,"2030년 종료 예정"],
    ["Project B","방산 프로젝트",97.94,147.00,75.00,"진행률 고점"],
], columns=["프로젝트","구분","진행률","계약자산_억원","매출채권_억원","메모"])

# -----------------------------
# 4. 계약 추정 변경
# 공개된 방산부문 예시
# 단위: 억원
# -----------------------------
estimate = pd.DataFrame([
    ["2023 H1", 552, 189, 188, 175],
    ["2025 H1", 593,-1061,465,1188],
], columns=["기간","총계약수익_추정변경","총계약원가_추정변경","당기손익_영향","미래손익_영향"])

# -----------------------------
# 공통 함수
# -----------------------------
def fmt(v, digits=0):
    if pd.isna(v): return "-"
    return f"{v:,.{digits}f}"

def risk_label(row):
    score = 0
    reasons = []
    if row["진행률"] >= 90 and row["매출채권_억원"] >= 50:
        score += 2; reasons.append("높은 진행률 대비 채권 잔액")
    if row["계약자산_억원"] >= 500:
        score += 2; reasons.append("계약자산 규모 큼")
    elif row["계약자산_억원"] >= 100:
        score += 1; reasons.append("계약자산 모니터링 필요")
    if score >= 3: level="집중관리"
    elif score >= 1: level="모니터링"
    else: level="양호"
    return pd.Series([level, ", ".join(reasons) if reasons else "특이 신호 없음"])

projects[["관리등급","자동진단"]] = projects.apply(risk_label, axis=1)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("분석 범위")
st.sidebar.markdown("**한화시스템 방산부문 관리회계**")
st.sidebar.caption("분석기간: 2023Q1 ~ 2026Q2")
page = st.sidebar.radio(
    "메뉴",
    ["Executive Summary","① 방산 성장·수익성","② 생산능력·가동률",
     "③ 프로젝트 진행·회수","④ 계약수익·원가 추정","⑤ 관리회계 종합진단","데이터·한계"]
)

st.sidebar.divider()
st.sidebar.caption("주의: 방산부문 영업현금흐름은 외부공시에서 별도 분리되지 않아 직접 산출하지 않습니다.")

# -----------------------------
# Executive Summary
# -----------------------------
if page == "Executive Summary":
    st.title("한화시스템 방산사업 관리회계 진단")
    st.caption("수주·생산·프로젝트·수익성·청구/회수 관점에서 방산사업의 성장의 질을 분석")

    latest = quarterly.iloc[-1]
    yoy = quarterly.iloc[-5]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("2026Q2 방산 매출", f"{latest['방산매출']:,.0f}억원",
              f"{latest['매출_YoY']:+.1f}% YoY")
    c2.metric("2026Q2 방산 영업이익", f"{latest['방산영업이익']:,.0f}억원",
              f"{latest['영업이익_YoY']:+.1f}% YoY")
    c3.metric("2026Q2 영업이익률", f"{latest['영업이익률']:.1f}%",
              f"{latest['OPM_변화_YoY']:+.1f}%p YoY")
    c4.metric("2026 H1 생산 가동률", "92.99%", "2025 FY 83.72%")

    st.subheader("핵심 판단")
    st.markdown("""
    <div class="good"><b>1. 수익성:</b> 2026Q2 방산 영업이익률은 14.8%로 분석기간 최고 수준입니다.
    회사는 수출사업 증가를 주요 원인으로 제시하고 있습니다.</div>
    <div class="insight"><b>2. 생산:</b> 생산능력 확대 이후 2026년 상반기 가동률이 92.99%까지 상승했습니다.
    향후 수주·매출 증가가 지속될 경우 생산능력과 납기 부담을 함께 볼 필요가 있습니다.</div>
    <div class="risk"><b>3. 프로젝트 관리:</b> 방산 장기계약은 진행률뿐 아니라 계약자산·매출채권과
    총계약수익/원가 추정 변경을 함께 봐야 실제 수익성과 회수 부담을 판단할 수 있습니다.</div>
    """, unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=quarterly["분기"], y=quarterly["방산매출"], name="방산 매출"))
    fig.add_trace(go.Scatter(x=quarterly["분기"], y=quarterly["영업이익률"],
                             name="영업이익률", yaxis="y2", mode="lines+markers"))
    fig.update_layout(height=430, yaxis_title="매출(억원)",
                      yaxis2=dict(title="영업이익률(%)", overlaying="y", side="right"),
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ① 성장/수익성
# -----------------------------
elif page == "① 방산 성장·수익성":
    st.title("① 방산 성장·수익성")
    st.write("방산 매출 성장 자체보다 **영업이익과 이익률이 함께 개선되는지**를 확인합니다.")

    metric = st.radio("차트 지표", ["매출·영업이익","영업이익률","YoY 성장률"], horizontal=True)

    if metric == "매출·영업이익":
        fig = go.Figure()
        fig.add_trace(go.Bar(x=quarterly["분기"], y=quarterly["방산매출"], name="매출"))
        fig.add_trace(go.Bar(x=quarterly["분기"], y=quarterly["방산영업이익"], name="영업이익"))
        fig.update_layout(barmode="group", height=470, yaxis_title="억원")
    elif metric == "영업이익률":
        fig = px.line(quarterly, x="분기", y="영업이익률", markers=True)
        fig.update_layout(height=470, yaxis_title="%")
    else:
        temp = quarterly.dropna(subset=["매출_YoY"]).copy()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=temp["분기"], y=temp["매출_YoY"], name="매출 YoY"))
        fig.add_trace(go.Bar(x=temp["분기"], y=temp["영업이익_YoY"], name="영업이익 YoY"))
        fig.update_layout(barmode="group", height=470, yaxis_title="%")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("분기별 원인")
    show = quarterly[["분기","방산매출","방산영업이익","영업이익률","회사제시_주요원인"]].copy()
    st.dataframe(show, use_container_width=True, hide_index=True)

    st.markdown("""
    **관리회계 포인트:** 매출 증가율만 보면 2025Q4가 가장 눈에 띄지만,
    영업이익률은 2026Q1~Q2에 크게 개선됩니다. 따라서 수출 Mix, 자체투자 개발비,
    판관비, 원가절감 등 **매출 구성과 비용 요인**을 분리해서 보는 것이 중요합니다.
    """)

# -----------------------------
# ② 생산
# -----------------------------
elif page == "② 생산능력·가동률":
    st.title("② 생산능력·가동률")
    st.write("수주와 매출 증가를 **생산능력이 실제로 뒷받침하고 있는지** 확인합니다.")

    c1,c2,c3 = st.columns(3)
    c1.metric("2023 FY 생산능력", "11,662억원")
    c2.metric("2025 FY 생산능력", "17,294억원", "+48.3% vs 2023")
    c3.metric("2026 H1 가동률", "92.99%", "+9.27%p vs 2025 FY")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=production["기간"], y=production["생산능력"], name="생산능력"))
    fig.add_trace(go.Bar(x=production["기간"], y=production["생산실적"], name="생산실적"))
    fig.add_trace(go.Scatter(x=production["기간"], y=production["가동률"], name="가동률",
                             yaxis="y2", mode="lines+markers"))
    fig.update_layout(height=480, barmode="group", yaxis_title="억원",
                      yaxis2=dict(title="가동률(%)", overlaying="y", side="right"))
    st.plotly_chart(fig, use_container_width=True)

    st.info("H1과 FY는 산출기간이 다르므로 생산능력·생산실적 금액을 단순 전기비교하지 않고, 가동률과 연간 추세를 함께 해석합니다.")

# -----------------------------
# ③ 프로젝트
# -----------------------------
elif page == "③ 프로젝트 진행·회수":
    st.title("③ 프로젝트 진행·청구·회수")
    st.write("장기 방산 프로젝트의 **진행률 → 계약자산(미청구) → 매출채권(청구 후 미회수)** 흐름을 봅니다.")

    st.dataframe(projects, use_container_width=True, hide_index=True)

    fig = px.scatter(projects, x="진행률", y="계약자산_억원",
                     size="매출채권_억원", hover_name="프로젝트",
                     hover_data=["관리등급","자동진단"])
    fig.update_layout(height=450, xaxis_title="진행률(%)", yaxis_title="계약자산(억원)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight"><b>해석 로직</b><br>
    ① 진행률 상승 + 계약자산 증가 → 수행한 작업 대비 청구 전 금액 증가 여부 확인<br>
    ② 높은 진행률 + 매출채권 잔액 지속 → 대금 회수 일정 점검<br>
    ③ 진행률 변화와 계약자산·채권 변화를 여러 분기에 걸쳐 함께 추적 → 프로젝트별 자금 묶임을 조기 식별
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# ④ 추정 변경
# -----------------------------
elif page == "④ 계약수익·원가 추정":
    st.title("④ 프로젝트 예상수익·예상원가 변화")
    st.write("방산 장기계약의 **총계약수익·총계약원가 추정 변경이 현재와 미래 손익에 미치는 영향**을 봅니다.")

    st.dataframe(estimate, use_container_width=True, hide_index=True)

    fig = go.Figure()
    for col in ["총계약수익_추정변경","총계약원가_추정변경","당기손익_영향","미래손익_영향"]:
        fig.add_trace(go.Bar(x=estimate["기간"], y=estimate[col], name=col))
    fig.update_layout(barmode="group", height=470, yaxis_title="억원")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **관리회계 포인트:** 실제 내부 예산은 공개되지 않으므로 ‘예산 대비 실적’을 임의로 만들지 않습니다.
    대신 공개된 장기계약의 **예상 수익·예상 원가 추정 변경**을 이용해 프로젝트 수익성 변화를 분석합니다.
    내부 예산 데이터가 입력되면 동일 구조에 예실차 분석을 추가할 수 있습니다.
    """)

# -----------------------------
# ⑤ 종합진단
# -----------------------------
elif page == "⑤ 관리회계 종합진단":
    st.title("⑤ 방산 관리회계 종합진단")

    latest = quarterly.iloc[-1]
    prev_y = quarterly.iloc[-5]

    st.subheader("자동 진단")
    messages = []
    if latest["매출_YoY"] > 20:
        messages.append(("성장","방산 매출이 전년 동기 대비 크게 증가했습니다. 증가 물량의 생산·납기 대응력을 함께 점검해야 합니다."))
    if latest["영업이익률"] > prev_y["영업이익률"]:
        messages.append(("수익성","영업이익률이 전년 동기보다 개선됐습니다. 회사 설명상 수출 매출 증가가 주요 요인입니다."))
    if production.iloc[-1]["가동률"] >= 90:
        messages.append(("생산","2026 H1 가동률이 90%를 상회합니다. 수주 확대가 지속될 경우 CAPA와 병목 공정을 모니터링할 필요가 있습니다."))
    if estimate.iloc[-1]["미래손익_영향"] > 0:
        messages.append(("프로젝트","최근 공개 사례에서 계약수익·원가 추정 변경의 미래손익 영향이 플러스입니다. 다만 개별 프로젝트별 변동 원인 확인이 필요합니다."))

    for title, msg in messages:
        st.markdown(f'<div class="insight"><b>{title}</b> — {msg}</div>', unsafe_allow_html=True)

    st.subheader("경영진에게 보고할 4가지 질문")
    st.markdown("""
    1. **수익성:** 수출 Mix 확대가 영업이익률 개선에 얼마나 기여했는가?
    2. **생산:** 현재 가동률 수준에서 추가 수주를 소화할 생산능력과 병목 여력은 충분한가?
    3. **프로젝트:** 총계약원가 추정이 크게 변한 프로젝트는 무엇이며 원인은 무엇인가?
    4. **회수:** 진행률 대비 계약자산·매출채권이 빠르게 증가하는 프로젝트는 무엇인가?
    """)

    st.subheader("프로그램의 최종 결론")
    st.success(
        "방산부문의 성장 여부를 매출 하나로 판단하지 않고, "
        "① 수익성 ② 생산능력 ③ 프로젝트 원가추정 ④ 청구·회수 신호를 연결해 "
        "성장의 질과 관리 필요 구간을 식별한다."
    )

# -----------------------------
# 데이터/한계
# -----------------------------
else:
    st.title("데이터·분석 한계")
    st.markdown("""
    **사용 자료**
    - 2023Q1~2026Q2 한화시스템 분기 실적발표 자료
    - 2023~2025 사업보고서 및 2023Q1~2026Q2 분기·반기보고서
    - 분석 대상은 **방산부문**으로 한정

    **중요한 한계**
    - 방산부문 영업활동현금흐름은 별도 공시되지 않아 임의 배분하지 않음
    - 전체 계약자산·계약부채를 방산 수치로 오인하지 않음
    - 프로젝트명은 보안상 A, B 등으로 표시되는 경우가 있어 공시된 범위만 사용
    - 내부 예산이 없으므로 실제 예산 대비 실적 차이를 임의 생성하지 않음
    - 프로젝트 데이터는 현재 공시에서 확인된 대표 사례를 넣었으며, 전체 프로젝트 시계열은 후속 확장 가능
    """)

    st.subheader("원천 분기 손익 데이터")
    st.dataframe(quarterly, use_container_width=True, hide_index=True)

    csv = quarterly.to_csv(index=False).encode("utf-8-sig")
    st.download_button("분기 손익 CSV 다운로드", csv, "hanwha_defense_quarterly.csv", "text/csv")
