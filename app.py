import streamlit as st

st.set_page_config(page_title="Risk Mühendisliği Skorlama Aracı", page_icon="🛡️", layout="centered")

QUESTIONS = [
    {
        "category": "Bina ve Konstrüksiyon",
        "question": "Ana yapı tipi nedir?",
        "options": {
            "Betonarme / yanmaz yapı": 10,
            "Çelik yapı": 7,
            "Sandviç panel / kısmen yanıcı": 3,
            "Ağırlıklı yanıcı yapı": 0,
        },
        "red_flags": ["Ağırlıklı yanıcı yapı"],
        "tips": {
            "Sandviç panel / kısmen yanıcı": "Yapı malzemeleri ve çatı detayları yeniden değerlendirilmelidir.",
            "Ağırlıklı yanıcı yapı": "Yanıcı yapı elemanları nedeniyle risk kabulü öncesi detaylı teknik inceleme önerilir.",
        },
    },
    {
        "category": "Yangın Koruma",
        "question": "Sprinkler sistemi durumu nedir?",
        "options": {
            "Tam sprinkler": 15,
            "Kısmi sprinkler": 8,
            "Yok": 0,
        },
        "red_flags": ["Yok"],
        "tips": {
            "Kısmi sprinkler": "Kritik alanlarda sprinkler kapsaması artırılmalıdır.",
            "Yok": "Sprinkler bulunmayan tesislerde kritik alanlar için aktif koruma önlemleri değerlendirilmelidir.",
        },
    },
    {
        "category": "Yangın Koruma",
        "question": "Yangın algılama ve ihbar sistemi durumu nedir?",
        "options": {
            "Adresli ve bakımlı": 10,
            "Temel sistem var": 6,
            "Sınırlı / yetersiz": 2,
            "Yok": 0,
        },
        "red_flags": ["Yok"],
        "tips": {
            "Sınırlı / yetersiz": "Algılama sistemi kapsama ve bakım yönünden iyileştirilmelidir.",
            "Yok": "Yangın algılama ve ihbar sistemi kurulması önerilir.",
        },
    },
    {
        "category": "Elektrik",
        "question": "Elektrik tesisatının genel durumu nasıldır?",
        "options": {
            "Yeni / düzenli kontrollü": 10,
            "Kabul edilebilir": 6,
            "Eski / düzensiz": 2,
            "Belirsiz / kötü": 0,
        },
        "red_flags": ["Belirsiz / kötü"],
        "tips": {
            "Eski / düzensiz": "Elektrik altyapısı için periyodik bakım ve kontrol planı oluşturulmalıdır.",
            "Belirsiz / kötü": "Elektrik panoları ve tesisat için acil teknik inceleme önerilir.",
        },
    },
    {
        "category": "Elektrik",
        "question": "Termal kamera ve pano kontrolleri yapılıyor mu?",
        "options": {
            "Düzenli ve kayıtlı": 10,
            "Aralıklı": 5,
            "Yapılmıyor": 0,
        },
        "red_flags": ["Yapılmıyor"],
        "tips": {
            "Aralıklı": "Termal tarama ve pano kontrolü düzenli kayıt altına alınmalıdır.",
            "Yapılmıyor": "Termal kamera ile periyodik pano kontrolleri başlatılmalıdır.",
        },
    },
    {
        "category": "Housekeeping",
        "question": "Temizlik ve genel düzen seviyesi nedir?",
        "options": {
            "Çok iyi": 10,
            "Orta": 6,
            "Zayıf": 2,
            "Çok zayıf": 0,
        },
        "red_flags": ["Çok zayıf"],
        "tips": {
            "Zayıf": "Housekeeping disiplini güçlendirilmelidir.",
            "Çok zayıf": "Yanıcı yük ve dağınıklık nedeniyle düzen ve temizlik aksiyonu öncelikli olmalıdır.",
        },
    },
    {
        "category": "Faaliyet / Proses",
        "question": "Faaliyet tipi tehlike seviyesi nedir?",
        "options": {
            "Düşük tehlike": 10,
            "Orta tehlike": 6,
            "Yüksek tehlike": 2,
            "Çok yüksek tehlike": 0,
        },
        "red_flags": ["Çok yüksek tehlike"],
        "tips": {
            "Yüksek tehlike": "Faaliyetin proses ve yangın maruziyeti için ek kontrol tedbirleri değerlendirilmelidir.",
            "Çok yüksek tehlike": "Yüksek tehlikeli faaliyet nedeniyle detaylı teknik değerlendirme ve sıkı şartlar önerilir.",
        },
    },
    {
        "category": "Acil Müdahale",
        "question": "En yakın itfaiyeye erişim nasıldır?",
        "options": {
            "Çok iyi / yakın": 10,
            "Orta": 6,
            "Uzak": 2,
            "Çok uzak / erişim sorunlu": 0,
        },
        "red_flags": ["Çok uzak / erişim sorunlu"],
        "tips": {
            "Uzak": "Tesis içi ilk müdahale kapasitesi güçlendirilmelidir.",
            "Çok uzak / erişim sorunlu": "İtfaiye erişim zayıflığı nedeniyle tesis içi acil müdahale organizasyonu güçlendirilmelidir.",
        },
    },
]

MAX_SCORE = sum(max(q["options"].values()) for q in QUESTIONS)


def get_risk_level(score_percent: float) -> tuple[str, str]:
    if score_percent >= 85:
        return "Çok İyi", "Risk genel olarak güçlü görünmektedir. Standart şartlarla değerlendirilebilir."
    elif score_percent >= 70:
        return "İyi", "Risk kabul edilebilir düzeydedir. Belirli iyileştirmeler önerilebilir."
    elif score_percent >= 50:
        return "Orta / Referral", "Risk için ek değerlendirme ve iyileştirme planı önerilir."
    elif score_percent >= 35:
        return "Zayıf / Üst Değerlendirme", "Belirgin eksiklikler vardır. Üst değerlendirme ve sıkı şartlar gerekebilir."
    return "Çok Zayıf / Decline Eğilimi", "Risk mevcut haliyle zayıf görünmektedir. Kritik iyileştirmeler sonrası yeniden değerlendirme uygun olabilir."


def main():
    st.title("🛡️ Risk Mühendisliği Skorlama Aracı")
    st.caption("Bu araç karar destek amaçlıdır. Nihai underwriting kararı uzman değerlendirmesi gerektirir.")

    with st.form("risk_form"):
        st.subheader("Risk Bilgileri")
        risk_name = st.text_input("Risk / Müşteri Adı")
        location = st.text_input("Lokasyon")
        activity = st.text_input("Faaliyet Türü")

        st.divider()
        st.subheader("Değerlendirme Soruları")

        answers = []
        for i, q in enumerate(QUESTIONS):
            st.markdown(f"**{i+1}. {q['question']}**")
            answer = st.radio(
                label=q["category"],
                options=list(q["options"].keys()),
                key=f"q_{i}",
                label_visibility="collapsed",
            )
            answers.append(answer)

        submitted = st.form_submit_button("Skoru Hesapla", use_container_width=True)

    if submitted:
        total_score = 0
        red_flags = []
        tips = []
        category_scores = {}

        for q, answer in zip(QUESTIONS, answers):
            score = q["options"][answer]
            total_score += score

            category = q["category"]
            category_scores[category] = category_scores.get(category, 0) + score

            if answer in q["red_flags"]:
                red_flags.append(f"{q['question']} → {answer}")

            if answer in q.get("tips", {}):
                tips.append(q["tips"][answer])

        score_percent = round((total_score / MAX_SCORE) * 100, 1)
        risk_level, uw_text = get_risk_level(score_percent)

        st.divider()
        st.subheader("Sonuç")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Toplam Skor", f"{score_percent} / 100")
        with col2:
            st.metric("Risk Seviyesi", risk_level)

        if risk_name or location or activity:
            st.markdown("### Risk Özeti")
            if risk_name:
                st.write(f"**Risk / Müşteri:** {risk_name}")
            if location:
                st.write(f"**Lokasyon:** {location}")
            if activity:
                st.write(f"**Faaliyet:** {activity}")

        st.markdown("### Kategori Bazlı Skorlar")
        for category, score in category_scores.items():
            st.write(f"- **{category}:** {score}")

        st.markdown("### Underwriting Değerlendirmesi")
        st.write(uw_text)

        st.markdown("### Kırmızı Bayraklar")
        if red_flags:
            for flag in red_flags:
                st.error(flag)
        else:
            st.success("Kritik seviyede otomatik kırmızı bayrak tespit edilmedi.")

        st.markdown("### Önerilen İyileştirme Aksiyonları")
        unique_tips = list(dict.fromkeys(tips))
        if unique_tips:
            for tip in unique_tips:
                st.write(f"- {tip}")
        else:
            st.write("- Belirgin bir iyileştirme aksiyonu oluşmadı.")

        st.markdown("### Genel Yorum")
        if red_flags and score_percent >= 70:
            st.warning("Skor kabul edilebilir görünse de kritik kırmızı bayraklar nedeniyle referral yaklaşımı uygun olabilir.")
        elif score_percent < 50:
            st.warning("Risk zayıf seviyededir. Ek bilgi, teknik inceleme ve iyileştirme planı önerilir.")
        else:
            st.info("Sonuç, mevcut cevaplara göre oluşturulmuştur. Gerekirse saha incelemesi ile teyit edilmelidir.")


if __name__ == "__main__":
    main()
