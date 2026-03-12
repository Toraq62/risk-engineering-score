import json
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Risk Mühendisliği Skorlama Aracı",
    page_icon="🛡️",
    layout="centered",
)

QUESTIONS_FILE = Path("questions.json")


def load_questions():
    if not QUESTIONS_FILE.exists():
        st.error("questions.json dosyası bulunamadı.")
        st.stop()

    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["questions"]
    except Exception as e:
        st.error(f"questions.json okunamadı: {e}")
        st.stop()


QUESTIONS = load_questions()
MAX_SCORE = sum(max(opt["score"] for opt in q["options"]) for q in QUESTIONS)


def get_base_risk_level(score_percent: float) -> str:
    if score_percent >= 85:
        return "Çok İyi"
    if score_percent >= 70:
        return "İyi"
    if score_percent >= 50:
        return "Orta"
    if score_percent >= 35:
        return "Zayıf"
    return "Çok Zayıf"


def evaluate_referral(answers_by_id: dict) -> tuple[bool, list[str]]:
    """
    Belirli kritik cevaplar varsa sonucu otomatik referral yap.
    """
    referral_reasons = []

    rules = {
        "Q2": "Yok",  # Sprinkler
        "Q3": "Yok",  # Algılama
        "Q5": "Yapılmıyor",  # Termal kamera / pano kontrolü
        "Q7": "Çok yüksek tehlike",  # Faaliyet
        "Q8": "Çok uzak / erişim sorunlu",  # İtfaiye erişimi
    }

    for question_id, trigger_answer in rules.items():
        selected = answers_by_id.get(question_id)
        if selected == trigger_answer:
            referral_reasons.append(f"{question_id} sorusunda kritik cevap: {trigger_answer}")

    is_referral = len(referral_reasons) > 0
    return is_referral, referral_reasons


def build_underwriting_text(
    score_percent: float,
    risk_level: str,
    is_referral: bool,
    red_flags: list[str],
) -> str:
    if is_referral:
        return (
            "Risk skoru tek başına değerlendirilmemelidir. Kritik koruma eksiklikleri ve/veya "
            "operasyonel zafiyetler nedeniyle standart kabul yerine referral değerlendirmesi önerilir. "
            "Ek bilgi, teknik inceleme ve gerekli risk iyileştirme aksiyonları sonrasında nihai underwriting "
            "kararı verilmesi uygundur."
        )

    if score_percent >= 85:
        return (
            "Mevcut bulgular çerçevesinde risk güçlü görünmektedir. Standart şartlarla değerlendirme "
            "yapılabilir."
        )
    if score_percent >= 70:
        return (
            "Risk genel olarak kabul edilebilir düzeydedir. Belirli iyileştirme önerileri poliçe öncesi "
            "veya poliçe dönemi içinde takip edilebilir."
        )
    if score_percent >= 50:
        return (
            "Risk orta seviyededir. Ek bilgi ve iyileştirme planı ile değerlendirme yapılması tavsiye edilir."
        )
    if score_percent >= 35:
        return (
            "Risk zayıf görünmektedir. Üst değerlendirme, sıkı şartlar ve belirli iyileştirme ön koşulları "
            "gerekebilir."
        )

    return (
        "Risk mevcut haliyle zayıf görünmektedir. Kritik eksikliklerin giderilmesi ve sonrasında yeniden "
        "değerlendirme yapılması önerilir."
    )


def main():
    st.title("🛡️ Risk Mühendisliği Skorlama Aracı")
    st.caption(
        "Bu araç karar destek amaçlıdır. Nihai underwriting kararı uzman değerlendirmesi gerektirir."
    )

    with st.form("risk_form"):
        st.subheader("Risk Bilgileri")
        risk_name = st.text_input("Risk / Müşteri Adı")
        location = st.text_input("Lokasyon")
        activity = st.text_input("Faaliyet Türü")

        st.divider()
        st.subheader("Değerlendirme Soruları")

        answers = []
        answers_by_id = {}

        for i, q in enumerate(QUESTIONS):
            st.markdown(f"**{i+1}. {q['question']}**")

            option_texts = [opt["text"] for opt in q["options"]]
            selected = st.radio(
                q["category"],
                options=option_texts,
                key=q["id"],
                label_visibility="collapsed",
            )

            answers.append(selected)
            answers_by_id[q["id"]] = selected

        submitted = st.form_submit_button("Skoru Hesapla", use_container_width=True)

    if submitted:
        total_score = 0
        red_flags = []
        tips = []
        category_scores = {}
        category_max_scores = {}

        for q, answer in zip(QUESTIONS, answers):
            matched_option = next(opt for opt in q["options"] if opt["text"] == answer)
            score = matched_option["score"]
            total_score += score

            category = q["category"]
            category_scores[category] = category_scores.get(category, 0) + score
            category_max_scores[category] = category_max_scores.get(category, 0) + max(
                opt["score"] for opt in q["options"]
            )

            if answer in q.get("red_flags", []):
                red_flags.append(f"{q['question']} → {answer}")

            if matched_option["score"] < max(opt["score"] for opt in q["options"]):
                tip = q.get("tip")
                if tip:
                    tips.append(tip)

        score_percent = round((total_score / MAX_SCORE) * 100, 1)
        base_risk_level = get_base_risk_level(score_percent)

        is_referral, referral_reasons = evaluate_referral(answers_by_id)

        final_risk_level = f"{base_risk_level} / Referral" if is_referral else base_risk_level
        uw_text = build_underwriting_text(score_percent, base_risk_level, is_referral, red_flags)

        st.divider()
        st.subheader("Sonuç")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Toplam Risk Skoru", f"{score_percent} / 100")
        with col2:
            st.metric("Risk Seviyesi", final_risk_level)

        if risk_name or location or activity:
            st.markdown("### Risk Özeti")
            if risk_name:
                st.write(f"**Risk / Müşteri:** {risk_name}")
            if location:
                st.write(f"**Lokasyon:** {location}")
            if activity:
                st.write(f"**Faaliyet Türü:** {activity}")

        st.markdown("### Kategori Bazlı Skorlar")
        for category, score in category_scores.items():
            max_cat = category_max_scores[category]
            pct = round((score / max_cat) * 100, 1) if max_cat else 0
            st.write(f"- **{category}:** {score} / {max_cat}  _( %{pct} )_")

        st.markdown("### Kritik Kırmızı Bayraklar")
        if red_flags:
            for flag in red_flags:
                st.error(flag)
        else:
            st.success("Kritik seviyede otomatik kırmızı bayrak tespit edilmedi.")

        if is_referral:
            st.markdown("### Referral Gerekçeleri")
            for reason in referral_reasons:
                st.warning(reason)

        st.markdown("### Önerilen Risk İyileştirme Aksiyonları")
        unique_tips = list(dict.fromkeys(tips))
        if unique_tips:
            for tip in unique_tips:
                st.write(f"- {tip}")
        else:
            st.write("- Belirgin bir iyileştirme aksiyonu oluşmadı.")

        st.markdown("### Underwriting Değerlendirmesi")
        st.write(uw_text)


if __name__ == "__main__":
    main()
