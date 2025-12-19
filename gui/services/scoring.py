from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from characterify.data.mbti_questions import questions as MBTI_QUESTIONS
from characterify.data.ocean_questions import ocean_questions as OCEAN_QUESTIONS
from characterify.data.enneagram_questions import enneagram_questions as ENNEAGRAM_QUESTIONS
from characterify.data.temperaments_questions import temperaments_questions as TEMPERAMENT_QUESTIONS


@dataclass(frozen=True)
class QuestionItem:
    trait: str
    text: str


@dataclass(frozen=True)
class TestDefinition:
    id: str
    title: str
    subtitle: str
    description: str
    instructions: List[str]
    questions: List[QuestionItem]
    scale_type: str  # "likert5"


class ScoringService:

    def get_tests(self) -> List[TestDefinition]:
        return [
            TestDefinition(
                id="mbti",
                title="MBTI",
                subtitle="Myers-Briggs Type Indicator",
                description=(
                    "Tes MBTI membantu Anda memahami preferensi alami dalam mendapatkan energi, memproses informasi, "
                    "mengambil keputusan, dan mengelola struktur hidup. Hasilnya bukan label benar/salah, melainkan "
                    "peta kecenderungan yang bisa dipakai untuk refleksi dan komunikasi."
                ),
                instructions=[
                    "Tidak ada jawaban benar atau salah. Pilih jawaban yang paling sesuai dengan diri Anda.",
                    "Jawablah secara jujur dan spontan, jangan terlalu lama berpikir.",
                    "Fokus pada kebiasaan umum Anda, bukan situasi khusus.",
                    "Durasi pengerjaan: ±10–15 menit.",
                ],
                questions=[QuestionItem(trait=t, text=q) for t, q in MBTI_QUESTIONS],
                scale_type="likert5",
            ),
            TestDefinition(
                id="ocean",
                title="Big Five (OCEAN)",
                subtitle="Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism",
                description=(
                    "Big Five memetakan kepribadian pada 5 dimensi yang banyak dipakai dalam riset psikologi. "
                    "Profil ini membantu memahami gaya kerja, relasi, cara belajar, dan strategi mengelola stres."
                ),
                instructions=[
                    "Gunakan skala 1–5 sesuai tingkat kesesuaian dengan diri Anda.",
                    "Jawab berdasarkan kebiasaan umum, bukan hari ini saja.",
                    "Tidak ada jawaban benar/salah.",
                    "Durasi: ±8–12 menit.",
                ],
                questions=[QuestionItem(trait=t, text=q) for t, q in OCEAN_QUESTIONS],
                scale_type="likert5",
            ),
            TestDefinition(
                id="enneagram",
                title="Enneagram",
                subtitle="9 Tipe Motivasi Inti",
                description=(
                    "Enneagram fokus pada motivasi inti, pola emosi, dan strategi bertahan saat tertekan. "
                    "Model ini cocok untuk refleksi diri, memahami pemicu, dan membentuk kebiasaan yang lebih sehat."
                ),
                instructions=[
                    "Jawab spontan: pilih yang paling menggambarkan diri Anda.",
                    "Fokus pada pola yang sering terjadi.",
                    "Gunakan skala 1–5.",
                    "Durasi: ±8–12 menit.",
                ],
                questions=[QuestionItem(trait=t, text=q) for t, q in ENNEAGRAM_QUESTIONS],
                scale_type="likert5",
            ),
            TestDefinition(
                id="temperament",
                title="4 Temperaments",
                subtitle="Sanguine, Choleric, Phlegmatic, Melancholic",
                description=(
                    "Tes Temperament memetakan kecenderungan energi dan gaya interaksi. "
                    "Hasilnya berguna untuk komunikasi, kerja tim, dan manajemen diri."
                ),
                instructions=[
                    "Jawab dengan jujur dan konsisten.",
                    "Gunakan skala 1–5.",
                    "Tidak ada jawaban benar/salah.",
                    "Durasi: ±5–8 menit.",
                ],
                questions=[QuestionItem(trait=t, text=q) for t, q in TEMPERAMENT_QUESTIONS],
                scale_type="likert5",
            ),
        ]


    # Scoring entrypoint
    def score_test(self, test_id: str, answers: Dict[int, int]) -> Dict[str, Any]:
        if test_id == "mbti":
            return self._score_mbti(answers)
        if test_id == "ocean":
            return self._score_ocean(answers)
        if test_id == "enneagram":
            return self._score_enneagram(answers)
        if test_id == "temperament":
            return self._score_temperament(answers)
        raise ValueError(f"Unknown test id: {test_id}")

    # MBTI
    def _score_mbti(self, answers: Dict[int, int]) -> Dict[str, Any]:
        scores = {k: 0 for k in ["I", "E", "N", "S", "T", "F", "P", "J"]}
        for i, (trait, _) in enumerate(MBTI_QUESTIONS):
            scores[trait] += int(answers.get(i, 0))

        code = ""
        code += "I" if scores["I"] >= scores["E"] else "E"
        code += "N" if scores["N"] >= scores["S"] else "S"
        code += "T" if scores["T"] >= scores["F"] else "F"
        code += "P" if scores["P"] >= scores["J"] else "J"

        dimensions = [
            ("I", "E", "Introvert", "Ekstrovert"),
            ("N", "S", "Intuitif", "Sensing"),
            ("T", "F", "Thinking", "Feeling"),
            ("P", "J", "Perceiving", "Judging"),
        ]

        dim_percentages: List[Dict[str, Any]] = []
        for a, b, name_a, name_b in dimensions:
            total = scores[a] + scores[b] or 1
            pct_a = scores[a] / total * 100
            pct_b = scores[b] / total * 100
            dim_percentages.append(
                {"a": a, "b": b, "name_a": name_a, "name_b": name_b, "pct_a": pct_a, "pct_b": pct_b}
            )

        content = self._mbti_content(code, dim_percentages)

        return {
            "test_id": "mbti",
            "result_type": code,
            "scores": scores,
            "percentages": dim_percentages,
            "chart_kind": "mbti_stacked",
            "content": content,
        }

    def _mbti_content(self, code: str, dims: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Nama populer + tagline singkat
        type_names = {
            "ISTJ": ("Logistician", "Terstruktur, realistis, dan konsisten menjaga standar."),
            "ISFJ": ("Defender", "Hangat, teliti, dan menjaga stabilitas serta kepedulian."),
            "INFJ": ("Advocate", "Visioner, idealis, peka pada makna dan nilai."),
            "INTJ": ("Strategist", "Analitis, mandiri, dan berorientasi sistem."),
            "ISTP": ("Virtuoso", "Praktis, tenang, unggul memecahkan masalah."),
            "ISFP": ("Adventurer", "Sensitif, fleksibel, dan autentik."),
            "INFP": ("Mediator", "Reflektif, empatik, dipandu nilai pribadi."),
            "INTP": ("Thinker", "Ingin tahu, logis, suka konsep mendalam."),
            "ESTP": ("Entrepreneur", "Berani, cepat, nyaman dengan dinamika."),
            "ESFP": ("Entertainer", "Energik, sosial, menciptakan suasana positif."),
            "ENFP": ("Campaigner", "Kreatif, antusias, mudah terhubung."),
            "ENTP": ("Debater", "Inovatif, kritis, suka eksplorasi ide."),
            "ESTJ": ("Executive", "Tegas, terorganisir, fokus hasil."),
            "ESFJ": ("Consul", "Ramah, suportif, menjaga harmoni."),
            "ENFJ": ("Protagonist", "Inspiratif, empatik, mendorong dampak."),
            "ENTJ": ("Commander", "Visioner, strategis, nyaman memimpin."),
        }

     
        long_desc = {
            "INTP": (
                "Sebagai INTP, Anda cenderung melihat dunia sebagai kumpulan konsep yang bisa dipahami dan dipetakan. "
                "Anda menikmati proses menganalisis, mencari pola, dan membangun penjelasan yang logis. Ketika menghadapi "
                "masalah, Anda lebih suka mengurai akar persoalan terlebih dahulu sebelum memberi solusi. Anda biasanya "
                "mandiri dalam belajar, menyukai kebebasan berpikir, dan bisa sangat produktif saat diberi ruang untuk "
                "bereksperimen. Tantangannya, Anda dapat menunda eksekusi ketika standar ‘jawaban sempurna’ belum tercapai, "
                "atau saat detail implementasi terasa membosankan. Dengan strategi sederhana seperti time-boxing dan "
                "komitmen pada versi pertama (draft), potensi analitis Anda bisa berubah menjadi output yang konsisten."
            )
        }

   
        def default_paragraph() -> str:
            return (
                f"Tipe {code} menggambarkan kombinasi preferensi yang memengaruhi cara Anda mengisi energi, memproses informasi, "
                "membuat keputusan, dan mengatur aktivitas. Anda cenderung memiliki pola yang cukup konsisten: apa yang membuat Anda "
                "cepat fokus, bagaimana Anda merespons tekanan, dan gaya komunikasi yang terasa natural. Hasil ini paling bermanfaat "
                "ketika Anda menggunakannya untuk memahami kekuatan sekaligus blind spot—misalnya kapan Anda perlu lebih banyak data, "
                "kapan perlu mempertimbangkan perasaan orang lain, atau kapan perlu menambah struktur agar rencana benar-benar jalan. "
                "Anggap tipe ini sebagai peta awal; Anda tetap bisa berkembang dengan melatih kebiasaan kecil yang menyeimbangkan preferensi."
            )

        name_en, tagline = type_names.get(code, (code, ""))
        paragraph = long_desc.get(code, default_paragraph())

        # Preferensi ringkas
        pref_map = {
            "I": "mengisi energi lewat waktu pribadi dan fokus mendalam",
            "E": "mengisi energi lewat interaksi dan stimulasi sosial",
            "S": "mengutamakan fakta, detail, dan langkah praktis",
            "N": "mengutamakan pola, kemungkinan, dan makna",
            "T": "mengambil keputusan lewat logika dan konsistensi",
            "F": "mengambil keputusan dengan mempertimbangkan nilai dan dampak emosional",
            "J": "menyukai struktur, rencana, dan kepastian",
            "P": "menyukai fleksibilitas, eksplorasi, dan opsi terbuka",
        }
        preference_notes = [pref_map.get(p, p) for p in list(code)]

        summary = (
            f"{code} — {name_en}\n\n"
            f"{paragraph}\n\n"
            f"Ringkas: Anda cenderung {preference_notes[0]}, {preference_notes[1]}, {preference_notes[2]}, dan {preference_notes[3]}.\n"
            f"Tagline: {tagline}"
        )

        def dominance_line(d: Dict[str, Any]) -> str:
            a = d["a"]
            b = d["b"]
            pct_a = float(d["pct_a"])
            pct_b = float(d["pct_b"])
            if pct_a >= pct_b:
                return f"{d['name_a']} lebih dominan (±{pct_a:.0f}%)."
            return f"{d['name_b']} lebih dominan (±{pct_b:.0f}%)."

        dim_insights = [f"{d['name_a']} vs {d['name_b']}: {dominance_line(d)}" for d in dims]

        strengths = [
            "Memiliki cara berpikir/bertindak yang konsisten sehingga mudah membangun gaya kerja yang kuat.",
            "Cenderung cepat memahami pola yang sesuai preferensi Anda (mis. data/detail atau gambaran besar/makna).",
            "Berpotensi tinggi dalam kolaborasi ketika peran dan ekspektasi jelas.",
        ]
        challenges = [
            "Risiko blind spot: terlalu nyaman pada preferensi sendiri sehingga kurang fleksibel.",
            "Di bawah tekanan, Anda bisa bereaksi ekstrem (mis. overthinking, overcontrol, atau menghindari konflik).",
            "Perbedaan gaya komunikasi dengan orang lain dapat memicu salah paham jika tidak diklarifikasi.",
        ]
        communication = [
            "Sampaikan konteks + tujuan + langkah berikutnya secara ringkas.",
            "Tanyakan kebutuhan lawan bicara (detail vs gambaran besar, cepat vs terstruktur).",
            "Biasakan klarifikasi: ulangi pemahaman Anda sebelum menyimpulkan.",
        ]
        teamwork = [
            "Ambil peran yang menguatkan preferensi Anda, namun latih 1 area kebalikan untuk keseimbangan.",
            "Gunakan ritme kerja: rencana singkat → eksekusi → review.",
            "Buat catatan/checklist agar progres lebih konsisten.",
        ]
        routines = [
            "Refleksi mingguan 10 menit: apa yang berjalan baik, pemicunya, dan 1 perbaikan kecil.",
            "Latih ‘pause 10 detik’ sebelum merespons situasi emosional atau konflik.",
            "Buat kebiasaan follow-up tertulis untuk mengurangi miskomunikasi.",
            "Kelola energi sesuai preferensi E/I (atur batas sosial atau waktu fokus).",
        ]

        return {
            "title": f"{code} — {name_en}",
            "subtitle": tagline,
            "summary_md": summary,
            "sections": [
                {"title": "Ringkasan Preferensi", "items": dim_insights},
                {"title": "Kekuatan Utama", "items": strengths},
                {"title": "Tantangan Umum", "items": challenges},
                {"title": "Saran Komunikasi", "items": communication},
                {"title": "Saran Karier & Kerja Tim", "items": teamwork},
                {"title": "Rutinitas Pengembangan Diri", "items": routines},
            ],
        }

# OCEAN
    def _score_ocean(self, answers: Dict[int, int]) -> Dict[str, Any]:
        scores = {k: 0 for k in ["O", "C", "E", "A", "N"]}
        for i, (trait, _) in enumerate(OCEAN_QUESTIONS):
            scores[trait] += int(answers.get(i, 0))

        values = [scores[k] for k in ["O", "C", "E", "A", "N"]]
        total = sum(values) or 1
        percentages = {k: scores[k] / total * 100 for k in scores}

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top1 = sorted_scores[0][0]
        top2 = sorted_scores[1][0]

        # gabungkan jika dekat
        if sorted_scores[0][1] - sorted_scores[1][1] <= 5:
            a, b = sorted([top1, top2])
            result_key = f"{a}_{b}"
        else:
            result_key = top1

        content = self._ocean_content(scores, percentages, result_key)

        return {
            "test_id": "ocean",
            "result_type": result_key,
            "scores": scores,
            "percentages": percentages,
            "chart_kind": "bar",
            "content": content,
        }

    def _ocean_content(self, scores: Dict[str, int], percentages: Dict[str, float], result_key: str) -> Dict[str, Any]:
        trait_names = {
            "O": "Openness",
            "C": "Conscientiousness",
            "E": "Extraversion",
            "A": "Agreeableness",
            "N": "Neuroticism",
        }


        desc_map = {
            "O": (
                "Openness tinggi biasanya terkait rasa ingin tahu, minat pada ide baru, dan kenyamanan mengeksplorasi kemungkinan. "
                "Anda cenderung menikmati belajar, mencoba pendekatan berbeda, dan melihat hubungan antar konsep. Di sisi lain, "
                "terlalu banyak eksplorasi bisa membuat Anda sulit menentukan pilihan. Kuncinya adalah membatasi eksplorasi dengan "
                "kriteria sederhana: ‘apa yang paling relevan dengan tujuan saya saat ini?’"
            ),
            "C": (
                "Conscientiousness tinggi menggambarkan kecenderungan untuk terstruktur, disiplin, dan fokus pada penyelesaian. "
                "Anda biasanya nyaman dengan rencana, checklist, dan target yang jelas. Ini sangat membantu untuk produktivitas, "
                "namun bisa berubah menjadi perfeksionisme atau rasa bersalah ketika target tidak tercapai. Strategi sehatnya adalah "
                "menerapkan standar ‘cukup baik’ dan menilai progres, bukan kesempurnaan."
            ),
            "E": (
                "Extraversion tinggi sering terlihat sebagai energi sosial, mudah memulai interaksi, dan nyaman berkomunikasi. "
                "Anda mungkin lebih mudah berpikir sambil berbicara dan mendapat motivasi dari lingkungan yang aktif. Tantangannya, "
                "Anda bisa cepat terdistraksi atau kelelahan jika jadwal terlalu padat. Mengatur jeda dan waktu fokus akan menjaga energi tetap stabil."
            ),
            "A": (
                "Agreeableness tinggi berkaitan dengan empati, kooperatif, dan kecenderungan menjaga harmoni. Anda biasanya peka pada kebutuhan orang lain "
                "dan mudah membangun suasana kerja yang suportif. Tantangannya, Anda dapat kesulitan berkata ‘tidak’ atau menghindari konflik penting. "
                "Latihan asertif yang sederhana—menyampaikan batas dengan kalimat singkat—akan membantu menjaga keseimbangan."
            ),
            "N": (
                "Neuroticism tinggi menunjukkan sensitivitas terhadap stres dan kecenderungan reaktif secara emosional. Ini bukan berarti ‘lemah’, "
                "tetapi sinyal bahwa sistem Anda cepat menangkap ancaman atau ketidakpastian. Kekuatan Anda adalah kepekaan terhadap risiko; tantangannya "
                "adalah mudah overthinking. Strategi yang efektif biasanya berupa rutinitas stabil, regulasi napas, dan memecah masalah menjadi langkah kecil."
            ),
        }

        combo = result_key.split("_")
        paragraphs = [desc_map.get(k, "") for k in combo if k in desc_map]
        if not paragraphs:
            paragraphs = [
                "Profil Big Five Anda relatif seimbang. Ini berarti Anda mungkin fleksibel menyesuaikan diri, namun tantangannya adalah menentukan fokus pengembangan. "
                "Pilih 1 dimensi yang paling relevan dengan tujuan saat ini (misalnya disiplin, komunikasi, atau manajemen stres), lalu latih dengan kebiasaan kecil selama 14 hari."
            ]

        # ringkasan skor
        per_trait = [f"{trait_names[k]}: ±{percentages[k]:.1f}%" for k in ["O", "C", "E", "A", "N"]]

        summary = (
            "Big Five (OCEAN)\n\n"
            + "\n\n".join([p for p in paragraphs if p]) + "\n\n"
            + "Ingat: hasil ini menggambarkan kecenderungan, bukan label mutlak. Gunakan sebagai peta untuk membuat strategi komunikasi, kerja, dan pengelolaan stres."
        )

        strengths = [
            "Membantu memahami gaya kerja & relasi berdasarkan 5 dimensi yang relatif stabil.",
            "Memetakan area pengembangan secara lebih terukur (mis. disiplin, empati, manajemen stres).",
            "Membantu menyusun kebiasaan yang sesuai dengan karakter Anda.",
        ]

        development: List[str] = []
        for t, pct in sorted(percentages.items(), key=lambda x: x[1], reverse=True):
            if pct >= 24:
                development.append(f"{trait_names[t]} cenderung tinggi: gunakan sebagai kekuatan, tapi jaga agar tidak berlebihan.")
            elif pct <= 16:
                development.append(f"{trait_names[t]} cenderung rendah: latih bertahap lewat kebiasaan kecil yang konsisten.")
        if not development:
            development.append("Skor cukup seimbang: fokus pada kebiasaan yang paling relevan dengan kebutuhan Anda saat ini.")

        routines = [
            "Pilih 1 dimensi untuk dilatih 14 hari (mis. Conscientiousness: checklist harian sederhana).",
            "Journaling 5 menit: pemicu emosi → respons → alternatif respons.",
            "Latih komunikasi: minta umpan balik singkat 1×/minggu dari orang tepercaya.",
        ]

        return {
            "title": "Big Five (OCEAN)",
            "subtitle": f"Profil dominan: {result_key}",
            "summary_md": summary,
            "sections": [
                {"title": "Skor Dimensi", "items": per_trait},
                {"title": "Manfaat Profil", "items": strengths},
                {"title": "Saran Pengembangan", "items": development},
                {"title": "Rutinitas Praktis", "items": routines},
            ],
        }


    # Enneagram
    def _score_enneagram(self, answers: Dict[int, int]) -> Dict[str, Any]:
        scores = {str(k): 0 for k in range(1, 10)}
        for i, (etype, _) in enumerate(ENNEAGRAM_QUESTIONS):
            scores[str(etype)] += int(answers.get(i, 0))

        result = max(scores, key=scores.get)
        total = sum(scores.values()) or 1
        percentages = {k: (v / total * 100) for k, v in scores.items()}

        content = self._enneagram_content(result)

        return {
            "test_id": "enneagram",
            "result_type": result,
            "scores": scores,
            "percentages": percentages,
            "chart_kind": "bar",
            "content": content,
        }

    def _enneagram_content(self, t: str) -> Dict[str, Any]:
        names = {
            "1": "The Reformer",
            "2": "The Helper",
            "3": "The Achiever",
            "4": "The Individualist",
            "5": "The Investigator",
            "6": "The Loyalist",
            "7": "The Enthusiast",
            "8": "The Challenger",
            "9": "The Peacemaker",
        }

        short = {
            "1": "Berorientasi prinsip, integritas, dan standar kualitas.",
            "2": "Hangat, suportif, dan termotivasi untuk membantu.",
            "3": "Berorientasi prestasi, citra, dan efektivitas.",
            "4": "Autentik, ekspresif, dan peka pada identitas.",
            "5": "Analitis, observatif, dan menghargai pengetahuan.",
            "6": "Loyal, waspada, dan butuh rasa aman.",
            "7": "Optimis, spontan, dan pencari pengalaman baru.",
            "8": "Tegas, protektif, dan menyukai kontrol.",
            "9": "Tenang, damai, dan mediator yang baik.",
        }

        long = {
            "1": (
                "Sebagai Type 1, Anda cenderung digerakkan oleh kebutuhan untuk ‘benar’ dan memperbaiki keadaan. Anda peka pada kesalahan, "
                "standar kualitas, dan nilai moral. Ini membuat Anda dapat diandalkan dan konsisten, namun bisa memicu kritik berlebihan "
                "pada diri sendiri atau orang lain. Kunci pertumbuhan Anda biasanya adalah self-compassion: membedakan standar sehat dengan "
                "perfeksionisme, serta menerima bahwa ‘cukup baik’ kadang lebih efektif daripada ‘sempurna’."
            ),
            "2": (
                "Sebagai Type 2, Anda mudah membaca kebutuhan orang lain dan merasa bermakna ketika bisa membantu. Anda membangun relasi dengan kehangatan "
                "dan dukungan, sehingga orang sering merasa aman di dekat Anda. Tantangannya, Anda bisa lupa kebutuhan sendiri atau mencari validasi lewat membantu. "
                "Pertumbuhan Type 2 biasanya datang dari batas sehat: berani berkata tidak, meminta bantuan, dan menghargai diri tanpa harus selalu memberi."
            ),
            "3": (
                "Sebagai Type 3, Anda terdorong untuk mencapai hasil dan terlihat kompeten. Anda biasanya adaptif, produktif, dan cepat membaca ekspektasi lingkungan. "
                "Di sisi lain, Anda dapat terjebak pada overwork atau terlalu menyamakan nilai diri dengan pencapaian. Pertumbuhan Type 3 muncul ketika Anda menyelaraskan "
                "tujuan eksternal dengan makna personal, serta menyediakan waktu pemulihan agar performa tetap berkelanjutan."
            ),
            "4": (
                "Sebagai Type 4, Anda peka pada emosi, identitas, dan keunikan diri. Anda cenderung mencari makna mendalam dan mengekspresikan diri secara autentik. "
                "Tantangannya, Anda bisa terjebak pada perasaan kurang atau membandingkan diri dengan orang lain. Pertumbuhan Type 4 biasanya muncul dari rutinitas yang stabil, "
                "aksi kecil yang konsisten, dan kemampuan melihat emosi sebagai informasi—bukan komando."
            ),
            "5": (
                "Sebagai Type 5, Anda termotivasi oleh kebutuhan memahami dan merasa kompeten melalui pengetahuan. Anda analitis, observatif, dan nyaman bekerja mandiri. "
                "Namun, Anda dapat menarik diri saat stres atau terlalu lama di tahap analisis hingga lupa bertindak. Pertumbuhan Type 5 sering terjadi ketika Anda menyeimbangkan "
                "teori dan praktik: berbagi pikiran, terlibat sosial secara bertahap, dan menguji ide melalui aksi."
            ),
            "6": (
                "Sebagai Type 6, Anda kuat dalam membaca risiko dan memikirkan skenario. Anda loyal, bertanggung jawab, dan sering menjadi ‘penjaga’ stabilitas tim. "
                "Tantangannya adalah kecemasan dan keraguan yang membuat keputusan terasa berat. Pertumbuhan Type 6 biasanya datang dari keberanian mencoba dengan rencana sederhana, "
                "uji asumsi lewat data, serta membangun kepercayaan pada proses."
            ),
            "7": (
                "Sebagai Type 7, Anda mencari kebebasan, pengalaman, dan kemungkinan baru. Anda optimis, cepat menemukan ide, dan mampu mengangkat mood. "
                "Tantangannya, Anda bisa menghindari ketidaknyamanan dan sulit fokus pada satu hal sampai tuntas. Pertumbuhan Type 7 muncul dari latihan fokus dan toleransi pada bosan: "
                "menyelesaikan satu hal penting sebelum pindah, serta memberi ruang untuk emosi yang kurang nyaman."
            ),
            "8": (
                "Sebagai Type 8, Anda cenderung tegas, protektif, dan nyaman mengambil kendali. Anda menghargai keadilan dan bisa menjadi pelindung bagi orang lain. "
                "Namun, Anda bisa terlihat keras atau sulit menunjukkan kerentanan. Pertumbuhan Type 8 biasanya datang dari latihan empati saat konflik, delegasi, dan keberanian "
                "mengungkap kebutuhan dengan cara yang lebih lembut."
            ),
            "9": (
                "Sebagai Type 9, Anda cenderung mencari kedamaian dan menjaga harmoni. Anda sabar, mampu menengahi, dan membuat suasana lebih stabil. "
                "Tantangannya, Anda bisa menunda, menghindari konflik, atau sulit menentukan prioritas. Pertumbuhan Type 9 sering terjadi ketika Anda melatih ketegasan kecil: "
                "menetapkan 1 prioritas harian, time-boxing, dan menyampaikan pendapat lebih awal."
            ),
        }

        strengths_map = {
            "1": ["Berintegritas", "Disiplin", "Dapat diandalkan"],
            "2": ["Empatik", "Dermawan", "Membangun relasi"],
            "3": ["Produktif", "Adaptif", "Berorientasi tujuan"],
            "4": ["Kreatif", "Peka emosi", "Autentik"],
            "5": ["Analitis", "Mandiri", "Objektif"],
            "6": ["Loyal", "Perencana", "Tanggung jawab"],
            "7": ["Optimis", "Inovatif", "Energik"],
            "8": ["Berani", "Tegas", "Melindungi"],
            "9": ["Menengahi", "Sabar", "Stabil"],
        }

        challenges_map = {
            "1": ["Perfeksionis", "Kritis", "Kaku"],
            "2": ["Sulit berkata tidak", "Terlalu mengutamakan orang", "Rentan kecewa"],
            "3": ["Overwork", "Terlalu fokus citra", "Mengabaikan emosi"],
            "4": ["Mood swing", "Membandingkan diri", "Overthinking"],
            "5": ["Menarik diri", "Overanalyze", "Sulit mengekspresikan emosi"],
            "6": ["Cemas", "Ragu", "Overprepare"],
            "7": ["Kurang fokus", "Impulsif", "Menghindari ketidaknyamanan"],
            "8": ["Dominan", "Keras", "Sulit rentan"],
            "9": ["Menunda", "Menghindari konflik", "Sulit prioritas"],
        }

        growth = {
            "1": ["Latih self-compassion", "Bedakan standar vs kontrol", "Izinkan 'cukup baik'"],
            "2": ["Tetapkan batas sehat", "Minta bantuan", "Validasi diri tanpa approval"],
            "3": ["Definisikan sukses versi diri", "Jadwalkan recovery", "Latih mindfulness"],
            "4": ["Rutinitas stabil", "Kelola emosi lewat jurnal", "Fokus aksi kecil konsisten"],
            "5": ["Seimbangkan teori & praktik", "Libatkan diri bertahap", "Bagikan pikiran sederhana"],
            "6": ["Uji asumsi lewat data", "Bangun rencana A/B", "Latih keberanian mencoba"],
            "7": ["Latih fokus 1 hal", "Toleransi bosan", "Selesaikan sebelum pindah"],
            "8": ["Latih empati saat konflik", "Delegasi & percaya", "Berani menunjukkan kebutuhan"],
            "9": ["Gunakan time-box", "Tentukan 1 prioritas/hari", "Latih konflik sehat"],
        }

        summary = (
            f"Enneagram Type {t} — {names.get(t, '')}\n\n"
            f"{long.get(t, short.get(t, ''))}\n\n"
            "Gunakan hasil ini untuk memahami motivasi inti dan pola respons Anda, terutama saat stres."
        )

        return {
            "title": f"Enneagram Type {t} — {names.get(t, '')}",
            "subtitle": short.get(t, ""),
            "summary_md": summary,
            "sections": [
                {"title": "Kekuatan", "items": strengths_map.get(t, [])},
                {"title": "Tantangan", "items": challenges_map.get(t, [])},
                {"title": "Saran Pengembangan", "items": growth.get(t, [])},
            ],
        }


    # Temperament
    def _score_temperament(self, answers: Dict[int, int]) -> Dict[str, Any]:
        scores = {k: 0 for k in ["S", "C", "P", "M"]}
        for i, (trait, _) in enumerate(TEMPERAMENT_QUESTIONS):
            scores[trait] += int(answers.get(i, 0))

        result = max(scores, key=scores.get)
        total = sum(scores.values()) or 1
        percentages = {k: (v / total * 100) for k, v in scores.items()}

        content = self._temperament_content(result)

        return {
            "test_id": "temperament",
            "result_type": result,
            "scores": scores,
            "percentages": percentages,
            "chart_kind": "bar",
            "content": content,
        }

    def _temperament_content(self, t: str) -> Dict[str, Any]:
        names = {"S": "Sanguine", "C": "Choleric", "P": "Phlegmatic", "M": "Melancholic"}

        long = {
            "S": (
                "Sanguine biasanya ditandai dengan energi sosial, antusiasme, dan ekspresi yang spontan. Anda cenderung mudah membangun koneksi dan membuat suasana menjadi hidup. "
                "Dalam kerja tim, Anda sering menjadi ‘penggerak mood’ dan pencetus interaksi. Tantangannya, Anda bisa cepat bosan atau terdistraksi. Strategi yang efektif adalah "
                "menggunakan struktur ringan (checklist singkat) dan time-boxing agar ide bisa berubah menjadi aksi."
            ),
            "C": (
                "Choleric cenderung tegas, fokus target, dan nyaman mengambil keputusan. Anda biasanya kuat dalam memimpin arah, mengeksekusi, dan menghadapi tekanan. "
                "Namun, Anda bisa terlihat terlalu dominan atau kurang sabar pada proses orang lain. Kunci pengembangan Anda adalah komunikasi yang lebih empatik: jelaskan ekspektasi, "
                "beri ruang diskusi, dan latih jeda sebelum merespons."
            ),
            "P": (
                "Phlegmatic cenderung tenang, kooperatif, dan menjaga harmoni. Anda sering menjadi penyeimbang dalam tim, sabar mendengar, serta mampu menengahi konflik. "
                "Tantangannya adalah menunda atau menghindari keputusan sulit. Pertumbuhan Anda muncul ketika Anda melatih ketegasan kecil: menetapkan prioritas harian dan berani menyampaikan pendapat lebih awal."
            ),
            "M": (
                "Melancholic biasanya teliti, terstruktur, dan peka pada kualitas. Anda cenderung nyaman dengan detail, analisis, dan standar yang jelas. Ini membuat Anda unggul dalam perencanaan dan quality control. "
                "Tantangannya, Anda bisa perfeksionis atau mudah cemas. Strategi sehatnya adalah memisahkan ‘standar’ dari ‘kontrol’, serta menerapkan batas waktu agar pekerjaan selesai tanpa menunggu sempurna."
            ),
        }

        desc = {
            "S": "Antusias, ekspresif, dan mudah membangun koneksi sosial.",
            "C": "Tegas, fokus tujuan, percaya diri, dan berorientasi hasil.",
            "P": "Tenang, kooperatif, dan menjaga harmoni.",
            "M": "Teliti, terstruktur, dan peka terhadap kualitas serta detail.",
        }

        strengths = {
            "S": ["Membangun suasana positif", "Komunikatif", "Cepat beradaptasi"],
            "C": ["Pemimpin alami", "Cepat mengambil keputusan", "Tangguh di bawah tekanan"],
            "P": ["Sabar", "Mediator", "Stabil"],
            "M": ["Detail-oriented", "Analitis", "Berstandar tinggi"],
        }
        challenges = {
            "S": ["Mudah terdistraksi", "Kurang konsisten", "Impulsif"],
            "C": ["Terlalu dominan", "Kurang sabar", "Terkesan keras"],
            "P": ["Menunda", "Menghindari konflik", "Kurang asertif"],
            "M": ["Perfeksionis", "Overthinking", "Rentan cemas"],
        }
        growth = {
            "S": ["Buat sistem sederhana (checklist)", "Time-box untuk fokus", "Evaluasi mingguan"],
            "C": ["Latih empati dalam komunikasi", "Delegasikan", "Gunakan jeda sebelum merespons"],
            "P": ["Tetapkan prioritas harian", "Latih berkata 'tidak'", "Konflik sehat bertahap"],
            "M": ["Latih 'cukup baik'", "Pisahkan fakta vs asumsi", "Atur ritme istirahat"],
        }

        summary = (
            f"{names.get(t, t)}\n\n"
            f"{long.get(t, desc.get(t, ''))}\n\n"
            "Temperament adalah gambaran kecenderungan energi dan interaksi. Anda tetap bisa mengembangkan kebiasaan yang menyeimbangkan gaya ini."
        )

        return {
            "title": f"{names.get(t, t)}",
            "subtitle": desc.get(t, ""),
            "summary_md": summary,
            "sections": [
                {"title": "Kekuatan", "items": strengths.get(t, [])},
                {"title": "Tantangan", "items": challenges.get(t, [])},
                {"title": "Saran Pengembangan", "items": growth.get(t, [])},
            ],
        }
