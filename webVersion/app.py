from flask import Flask, render_template, request
from questions import questions
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from temperaments_questions import temperaments_questions
from enneagram_questions import enneagram_questions
from temperament_result import deskripsi
from ocean_questions import ocean_questions

app = Flask(__name__)

CHART_DIR = os.path.join(app.static_folder, "charts")
os.makedirs(CHART_DIR, exist_ok=True)
#home
@app.route("/")
def index():
    return render_template("index.html")

#Test
@app.route("/test")
def test():
    return render_template("test.html")
    

#listTest
@app.route("/listtest")
def listtest():
    return render_template("listtest.html")

#about
@app.route("/about")
def about():
    return render_template("about.html")

#learn
@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/artikel1")
def artikel1():
    return render_template("learn/artikel1.html")

@app.route("/artikel2")
def artikel2():
    return render_template("learn/artikel2.html")

@app.route("/artikel3")
def artikel3():
    return render_template("learn/artikel3.html")

@app.route("/artikel4")
def artikel4():
    return render_template("learn/artikel4.html")

@app.route("/artikel5")
def artikel5():
    return render_template("learn/artikel5.html")

@app.route("/artikel6")
def artikel6():
    return render_template("learn/artikel6.html")

@app.route("/artikel7")
def artikel7():
    return render_template("learn/artikel7.html")

@app.route("/artikel8")
def artikel8():
    return render_template("learn/artikel8.html")

@app.route("/artikel9")
def artikel9():
    return render_template("learn/artikel9.html")

@app.route("/artikel10")
def artikel10():
    return render_template("learn/artikel10.html")

#panduan
@app.route("/panduan")
def panduan():
    return render_template("help/panduan.html")

@app.route("/FAQ")
def FAQ():
    return render_template("help/FAQ.html")






#MBTI
# ------------------------------
#  MBTI TEST ROUTING
# ------------------------------

@app.route("/beforembti")
def beforembti():
    return render_template("beforetest/beforembti.html")

@app.route("/script")
def script():
    return render_template("script.js")
@app.route("/survey")
def survey():
    return render_template("tes/mbti.html", questions=questions)


@app.route("/result", methods=["POST"])
def mbti_result():

    # Hitung skor dasar semua trait
    scores = {
        "I": 0, "E": 0,
        "N": 0, "S": 0,
        "T": 0, "F": 0,
        "P": 0, "J": 0
    }

    # Loop soal & masukkan ke skor
    for i, (trait, _) in enumerate(questions):
        answer = int(request.form.get(f"q{i}", 0))
        scores[trait] += answer

    # TENTUKAN 4 PASANG DIMENSI


    result = ""
    result += "I" if scores["I"] >= scores["E"] else "E"
    result += "N" if scores["N"] >= scores["S"] else "S"
    result += "T" if scores["T"] >= scores["F"] else "F"
    result += "P" if scores["P"] >= scores["J"] else "J"

    # CHART 2-WARNA PER BAR


    dimensions = [
        ("I", "E", "Introvert", "Extrovert", "#00cc99", "#cc66cc"),
        ("N", "S", "Intuitive", "Sensing", "#00cc99", "#cc66cc"),
        ("T", "F", "Thinking", "Feeling", "#00cc99", "#cc66cc"),
        ("P", "J", "Perceiving", "Judging", "#00cc99", "#cc66cc")
    ]

    labels = [f"{d1_name} vs {d2_name}" for _, _, d1_name, d2_name, _, _ in dimensions]

    plt.figure(figsize=(7, 4.5))

    y_pos = range(len(dimensions))

    for i, (t1, t2, name1, name2, color1, color2) in enumerate(dimensions):

        total = scores[t1] + scores[t2]
        if total == 0:
            total = 1

        pct1 = (scores[t1] / total) * 100
        pct2 = (scores[t2] / total) * 100

        # Bar kiri (trait 1)
        plt.barh(i, pct1, color=color1)

        # Bar kanan (trait 2) disambung dari bar 1
        plt.barh(i, pct2, left=pct1, color=color2)

        # Tulis teks di dalam bar
        plt.text(pct1 / 2, i, f"{name1} {pct1:.0f}%", ha="center", va="center", color="white", fontsize=10)
        plt.text(pct1 + pct2 / 2, i, f"{name2} {pct2:.0f}%", ha="center", va="center", color="white", fontsize=10)

    plt.xlim(0, 100)
    plt.yticks(y_pos, labels, fontsize=11)
    plt.xlabel("Persentase (%)")
    plt.grid(False)
    plt.box(False)

    chart_filename = "mbti_chart.png"
    chart_path = os.path.join(CHART_DIR, chart_filename)
    plt.savefig(chart_path, bbox_inches="tight", transparent=True)

    # 16 FILE HASIL
 

    file_map = {
        "ISTJ": "mbti_result/ISTJ.html",
        "ISFJ": "mbti_result/ISFJ.html",
        "INFJ": "mbti_result/INFJ.html",
        "INTJ": "mbti_result/INTJ.html",

        "ISTP": "mbti_result/ISTP.html",
        "ISFP": "mbti_result/ISFP.html",
        "INFP": "mbti_result/INFP.html",
        "INTP": "mbti_result/INTP.html",

        "ESTP": "mbti_result/ESTP.html",
        "ESFP": "mbti_result/ESFP.html",
        "ENFP": "mbti_result/ENFP.html",
        "ENTP": "mbti_result/ENTP.html",

        "ESTJ": "mbti_result/ESTJ.html",
        "ESFJ": "mbti_result/ESFJ.html",
        "ENFJ": "mbti_result/ENFJ.html",
        "ENTJ": "mbti_result/ENTJ.html"
    }

    return render_template(
        file_map[result],
        result=result,
        scores=scores,
        chart="charts/mbti_chart.png"
    )


# 4 Tempraments
@app.route("/temperament")
def temperament_test():
    return render_template("tes/temperament.html", temperaments_questions=temperaments_questions)

@app.route("/beforetemperament")
def beforetemperament():
    return render_template("beforetest/beforetemperament.html")

@app.route("/temperament_result", methods=["POST"])
def temperament_result():
    scores = {"S": 0, "C": 0, "P": 0, "M": 0}

    for i, (trait, _) in enumerate(temperaments_questions):
        answer = int(request.form.get(f"q{i}", 0))
        scores[trait] += answer

    # tentukan tipe tertinggi
    result = max(scores, key=scores.get)

    names = {
        "S": "Sanguine",
        "C": "Choleric",
        "P": "Phlegmatic",
        "M": "Melancholic",
    }

    labels = ["Sanguine", "Choleric", "Phlegmatic", "Melancholic"]
    values = [scores["S"], scores["C"], scores["P"], scores["M"]]

    total = sum(values)
    if total == 0:
        total = 1  # hindari error jika semua 0

    percentages = [(v / total) * 100 for v in values]

    plt.figure(figsize=(6, 4))

    bars = plt.barh(
        labels,
        percentages,
        color=["#ffcc00", "#ff6666", "#66cccc", "#9999ff"]
    )

    # Hilangkan grid & sumbu
    plt.grid(False)
    plt.xticks([])     # hilangkan angka X
    plt.yticks(fontsize=12)
    plt.box(False)

    # Tulis persentase di ujung bar
    for bar, pct in zip(bars, percentages):
        plt.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height()/2,
            f"{pct:.1f}%",
            va="center",
            fontsize=11
        )

    chart_filename = "temperament_chart.png"
    chart_path = os.path.join(CHART_DIR, chart_filename)
    plt.savefig(chart_path, bbox_inches="tight", transparent=True)


    file_map = {
        "S": "temperament_result/sanguine.html",
        "C": "temperament_result/choleric.html",
        "P": "temperament_result/phlegmatic.html",
        "M": "temperament_result/melancholic.html"
    } 

    return render_template(
        file_map[result],
        result=names[result],
        scores=scores,
        percentages=percentages,
        chart="charts/temperament_chart.png"
    )

#Enneagram
@app.route("/enneagram")
def enneagram_test():
    return render_template("tes/enneagram.html", enneagram_questions=enneagram_questions)

@app.route("/beforeennegram")
def enneagram_before():
    return render_template("beforetest/beforeennegram.html", enneagram_questions=enneagram_questions)

@app.route("/enneagram_result", methods=["POST"])
def enneagram_result():

    # 1. Skor awal
    scores = {
        "1": 0,"2": 0,"3": 0,"4": 0,"5": 0,
        "6": 0,"7": 0,"8": 0,"9": 0,
    }

    for i, (etype, _) in enumerate(enneagram_questions):
        answer = int(request.form.get(f"q{i}", 0))
        scores[etype] += answer

    # 2. Tentukan tipe dominan
    result = max(scores, key=scores.get)

    enneagram_names = {
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

    # 3. Generate chart 
    labels = [
    "The Reformer",
    "The Helper",
    "The Achiever",
    "The Individualist",
    "The Investigator",
    "The Loyalist",
    "The Enthusiast",
    "The Challenger",
    "The Peacemaker"
    ]

    values = [
        scores["1"], scores["2"], scores["3"],
        scores["4"], scores["5"], scores["6"],
        scores["7"], scores["8"], scores["9"]
    ]

    total = sum(values)
    if total == 0:
        total = 1

    percentages = [(v / total) * 100 for v in values]

    colors = [
        "#ff6666", "#ff9966", "#ffcc66",
        "#ccff66", "#66ff99", "#66ffcc",
        "#66ccff", "#6699ff", "#9966ff"
    ]
    labels = labels[::-1]
    percentages = percentages[::-1]
    colors = colors[::-1]

    plt.figure(figsize=(6, 4))
    bars = plt.barh(labels, percentages, color=colors)

    plt.grid(False)
    plt.xticks([])
    plt.yticks(fontsize=12)
    plt.box(False)

    for bar, pct in zip(bars, percentages):
        plt.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height()/2,
            f"{pct:.1f}%",
            va="center",
            fontsize=11
        )

    chart_filename = "enneagram_chart.png"
    chart_path = os.path.join(CHART_DIR, chart_filename)
    plt.savefig(chart_path, bbox_inches="tight", transparent=True)


    # 4. File map seperti OCEAN
    file_map = {
        "1": "enneagram_result/type1.html",
        "2": "enneagram_result/type2.html",
        "3": "enneagram_result/type3.html",
        "4": "enneagram_result/type4.html",
        "5": "enneagram_result/type5.html",
        "6": "enneagram_result/type6.html",
        "7": "enneagram_result/type7.html",
        "8": "enneagram_result/type8.html",
        "9": "enneagram_result/type9.html"
    }

    return render_template(
        file_map[result],
        result=enneagram_names[result],
        scores=scores,
        percentages=percentages,
        chart="charts/enneagram_chart.png"
    )


#OCEAN
@app.route("/beforeocean")
def beforeocean():
    return render_template("beforetest/beforeocean.html")


@app.route("/ocean")
def ocean_test():
    return render_template("tes/ocean.html", ocean_questions=ocean_questions)


@app.route("/ocean_result", methods=["POST"])
def ocean_result():
    # inisialisasi skor
    scores = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}

    # ambil semua jawaban
    for i, (trait, _) in enumerate(ocean_questions):
        ans = int(request.form.get(f"q{i}", 0))
        scores[trait] += ans

    # hitung total untuk persentase
    values = [scores["O"], scores["C"], scores["E"], scores["A"], scores["N"]]
    total = sum(values)
    if total == 0:
        total = 1

    percentages = [(v / total) * 100 for v in values]

    # buat chart horizontal
    labels = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
    plt.figure(figsize=(6, 4))
    bars = plt.barh(labels, percentages, color=["#0099ff", "#ffaa00", "#ff4444", "#44cc88", "#aa66ff"])

    plt.grid(False)
    plt.xticks([])
    plt.box(False)

    for bar, pct in zip(bars, percentages):
        plt.text(bar.get_width() + 1,
                 bar.get_y() + bar.get_height()/2,
                 f"{pct:.1f}%",
                 va="center",
                 fontsize=11)

    chart_filename = "ocean_chart.png"
    chart_path = os.path.join(CHART_DIR, chart_filename)
    plt.savefig(chart_path, bbox_inches="tight", transparent=True)


    # tentukan tipe utama
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top1 = sorted_scores[0][0]
    top2 = sorted_scores[1][0]

    # cek kombinasi (selisih ≤ 10%)
    if sorted_scores[0][1] - sorted_scores[1][1] <= 5:
        raw_key = f"{top1}_{top2}"       # contoh: N_O
        a, b = raw_key.split("_")
        result_key = "_".join(sorted([a, b]))   # contoh: O_N
    else:
        result_key = top1 

    # map ke file html
    file_map = {
    "O": "ocean_result/openness.html",
    "C": "ocean_result/conscientiousness.html",
    "E": "ocean_result/extraversion.html",
    "A": "ocean_result/agreeableness.html",
    "N": "ocean_result/neuroticism.html",

    # kombinasi (selalu alfabet)
    "A_C": "ocean_result/combo_A_C.html",
    "A_E": "ocean_result/combo_A_E.html",
    "A_N": "ocean_result/combo_A_N.html",
    "A_O": "ocean_result/combo_A_O.html",
    "C_E": "ocean_result/combo_C_E.html",
    "C_N": "ocean_result/combo_C_N.html",
    "C_O": "ocean_result/combo_C_O.html",
    "E_N": "ocean_result/combo_E_N.html",
    "E_O": "ocean_result/combo_E_O.html",
    "N_O": "ocean_result/combo_N_O.html"
}


    return render_template(
        file_map[result_key],
        scores=scores,
        percentages=percentages,
        chart="charts/ocean_chart.png",
        top_traits=result_key
    )


if __name__ == "__main__":
    app.run(debug=True)
