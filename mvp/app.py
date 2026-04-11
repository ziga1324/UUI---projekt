"""
ZestQuest - Flask Backend
=========================
Zaženi:
    pip install flask scikit-learn pandas numpy
    python app.py

Odpri brskalnik: http://localhost:5000
"""

import os, sys, json, random

# ── Absolutna pot do te datoteke (deluje ne glede od kod zaženemo) ─────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, request, jsonify, session
from model_helper import ZestQuestPredictor

# Flask z eksplicitno potjo do templates/
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = "zestquest-secret-2026"

# Naloži model – pokaže jasno napako če .pkl datoteke manjkajo
try:
    predictor = ZestQuestPredictor(BASE_DIR)
    print("✅ AI model uspešno naložen.")
except FileNotFoundError as e:
    print(f"\n❌ NAPAKA: {e}")
    print("   Najprej generiraj in treniraj model:")
    print("   python generiraj_podatke.py")
    print("   python treniraj_model.py --model gb\n")
    predictor = None

# ─── Baza sidequestov ──────────────────────────────────────────────────────────

SIDEQUESTI = {
    "kreativno": [
        {"naslov": "Nariši svoje razpoloženje", "opis": "Vzemi papir in barvice — nariši abstraktno sliko tega, kako se počutiš zdaj. Ni treba, da je lepo.", "cas": "10 min", "xp": 50},
        {"naslov": "Napiši pesem v 6 vrsticah", "opis": "Izberi predmet pred seboj in mu posveti kratko pesem. Nobenih pravil, samo besede.", "cas": "8 min", "xp": 60},
        {"naslov": "Fotografiraj 3 zanimive sence", "opis": "Pojdi po sobi ali ven in poisci 3 sence, ki izgledajo nenavadno ali lepo.", "cas": "5 min", "xp": 40},
        {"naslov": "Preuredi polico ali mizo", "opis": "Uredi predmete pred seboj po barvi, velikosti ali nekem svojem sistemu.", "cas": "10 min", "xp": 45},
        {"naslov": "Izmisli si novo jed", "opis": "Poglej v hladilnik in sestavi recept za jed, ki je še nisi nikoli naredil.", "cas": "5 min", "xp": 55},
    ],
    "gibanje": [
        {"naslov": "7-minutna raztezna rutina", "opis": "Raztegovaj vsak del telesa po 30 sekund. Začni z vratom, konča z glenji.", "cas": "7 min", "xp": 70},
        {"naslov": "Pojdi ven in poglej nebo", "opis": "Hodi 5 minut brez telefona. Poglej samo nebo in opazuj oblake ali zvezde.", "cas": "5 min", "xp": 50},
        {"naslov": "Naredi 20 poskokov", "opis": "Vstani in naredi 20 jumping jackov. Takoj bos bolj zbuden/a.", "cas": "2 min", "xp": 35},
        {"naslov": "Plesi na eno pesem", "opis": "Izberi svojo najljubšo pesem in plesi dokler ne konca. Solo disko v dnevni sobi.", "cas": "4 min", "xp": 65},
        {"naslov": "Sprehod do najblizjega koticka narave", "opis": "Pojdi do bliznjega parka, gozdica ali travnika. Samo hodi in disi zrak.", "cas": "20 min", "xp": 90},
    ],
    "socialno": [
        {"naslov": "Posji sporocilo osebi, ki te veseli", "opis": "Napisi kratko sporocilo nekomu, ki te ze dolgo ni slisal. Samo Hej, mislil sem na tebe!", "cas": "3 min", "xp": 55},
        {"naslov": "Pohvali nekoga danes", "opis": "Iskreno pohvali osebo, ki jo danes srecias ali vidis. Konkretno — kaj ti je pri njej vsec.", "cas": "1 min", "xp": 70},
        {"naslov": "Poklici starse ali brata/sestro", "opis": "Samo kratki klic — brez razloga, samo da slisis glas.", "cas": "10 min", "xp": 80},
        {"naslov": "Predlagaj druzenje prijateljem", "opis": "Posji sporocilo v skupino in predlagaj konkreten plan — kdaj, kje, kaj.", "cas": "5 min", "xp": 60},
        {"naslov": "Nasmehni se neznancu", "opis": "Ko gres ven, se nasmehni prvi osebi, ki jo srečaš. Opazuj reakcijo.", "cas": "5 min", "xp": 45},
    ],
    "ucenje": [
        {"naslov": "Nauci se 5 besed v tujem jeziku", "opis": "Izberi jezik, ki te zanima. Poisci 5 besed in si jih zapomni s ponovitvami.", "cas": "10 min", "xp": 65},
        {"naslov": "Preberi en Wikipedia clanek do konca", "opis": "Klikni na Random article in preberi kar dobiš. Zagotovo se bos kaj naucil/a.", "cas": "8 min", "xp": 55},
        {"naslov": "Oglej si kratek YouTube tutorial", "opis": "Poisci learn X in 5 minutes za karkoli, kar ti pride na misel.", "cas": "10 min", "xp": 60},
        {"naslov": "Resi eno logicno uganko", "opis": "Poisci sudoku ali krizanko in jo resi brez pomoci.", "cas": "15 min", "xp": 75},
        {"naslov": "Napisi 3 stvari, ki si se jih naucil danes", "opis": "Samo 3 — iz kateregakoli dela dneva. Malo, a dragoceno.", "cas": "5 min", "xp": 50},
    ],
    "sprostitev": [
        {"naslov": "5-minutna meditacija z dihanjem", "opis": "Zapri oci. Vdih 4 sekunde, zadrzij 4, izdih 6. Ponovi 10x. Nic drugega.", "cas": "5 min", "xp": 60},
        {"naslov": "Pripravi si toplo pijaco in samo sedi", "opis": "Caj, kava, kakav — karkoli. Brez telefona, brez glasbe. Samo pi in bodi.", "cas": "10 min", "xp": 50},
        {"naslov": "Zapiski hvaleznosti — 3 stvari", "opis": "Zapisi 3 zelo konkretne stvari, za katere si danes hvalezen/hvalezna.", "cas": "5 min", "xp": 55},
        {"naslov": "Poslušaj eno glasbo z zaprtimi ocmi", "opis": "Izberi pesem, lezi ali sedi, zapri oci in samo poslušaj — do konca.", "cas": "4 min", "xp": 45},
        {"naslov": "Izklopi vse obvestila za 30 minut", "opis": "Nacin ne moti. Nic nujnega ne bo. Samo ti in mir.", "cas": "30 min", "xp": 80},
    ],
    "pustolovscina": [
        {"naslov": "Pojdi tja, kjer se nikoli nisi bil", "opis": "V tvojem mestu gotovo obstaja ulica ali park, ki si jo/ga presockil. Pojdi tja zdaj.", "cas": "20 min", "xp": 100},
        {"naslov": "Naroci hrano, ki je se nisi preizkusil", "opis": "Izberi kuhinjo sveta, ki ti je tuja. Naroci. Brez branja menijev — samo en nakljucen izbor.", "cas": "5 min", "xp": 75},
        {"naslov": "Poisci skrito umetnost v mestu", "opis": "Street art, mozaik, fontana — poisci nekaj lepega, kar vecina sprehajalcev ne opazi.", "cas": "15 min", "xp": 85},
        {"naslov": "Vzemi nakljucen produkt s police", "opis": "V ziviljski izberi en produkt iz police brez da pogledas kaj je — samo prime in vzemi.", "cas": "10 min", "xp": 70},
        {"naslov": "Ustvari kratek vlog za sebe", "opis": "Posnemi 60-sekundni video o tem, kaj delas danes. Ne za objavo — samo zase.", "cas": "10 min", "xp": 80},
    ],
}

IKONE_KATEGORIJ = {
    "kreativno": "🎨",
    "gibanje": "⚡",
    "socialno": "💬",
    "ucenje": "📚",
    "sprostitev": "🌿",
    "pustolovscina": "🧭",
}

# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "xp" not in session:
        session["xp"] = 0
        session["streak"] = 0
        session["opravljeni"] = 0
    return render_template("index.html",
        xp=session["xp"],
        streak=session["streak"],
        opravljeni=session["opravljeni"],
    )

@app.route("/api/napovej", methods=["POST"])
def napovej():
    if predictor is None:
        return jsonify({"ok": False, "napaka": "Model ni nalozin. Pozeni treniraj_model.py --model gb"}), 500
    data = request.get_json(force=True, silent=True) or {}
    try:
        rezultat = predictor.napovej({
            "osebnost":          data.get("osebnost", "ambivert"),
            "cas_dneva":         data.get("cas_dneva", "popoldne"),
            "vreme":             data.get("vreme", "oblacno"),
            "energija":          data.get("energija", "srednja"),
            "lokacija":          data.get("lokacija", "doma"),
            "razpolozenje":      data.get("razpolozenje", "dolgcas"),
            "skupina":           data.get("skupina", "sam"),
            "cas_razpolozljiv":  data.get("cas_razpolozljiv", "15_30min"),
            "starost":           int(data.get("starost", 20)),
            "xp_skupaj":         int(session.get("xp", 0)),
            "streak_dni":        int(session.get("streak", 0)),
            "opravljeni_questi": int(session.get("opravljeni", 0)),
        })
        kategorija = rezultat["kategorija"]
        quest = random.choice(SIDEQUESTI[kategorija])
        return jsonify({
            "ok": True,
            "kategorija": kategorija,
            "ikona": IKONE_KATEGORIJ[kategorija],
            "quest": quest,
            "top3": rezultat["top3"],
            "verjetnosti": rezultat["verjetnosti"],
        })
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"ok": False, "napaka": str(e)}), 400

@app.route("/api/opravi", methods=["POST"])
def opravi():
    data = request.get_json(force=True, silent=True) or {}
    xp_zasluzeno = int(data.get("xp", 50))
    session["xp"]         = session.get("xp", 0) + xp_zasluzeno
    session["opravljeni"] = session.get("opravljeni", 0) + 1
    session["streak"]     = session.get("streak", 0) + 1
    session.modified = True
    return jsonify({
        "ok": True,
        "xp_skupaj":    session["xp"],
        "opravljeni":   session["opravljeni"],
        "streak":       session["streak"],
        "xp_zasluzeno": xp_zasluzeno,
    })

@app.route("/api/preskoci", methods=["POST"])
def preskoci():
    session["streak"] = max(0, session.get("streak", 1) - 1)
    session.modified = True
    return jsonify({"ok": True, "streak": session["streak"]})

@app.route("/api/reset", methods=["POST"])
def reset():
    session["xp"] = 0
    session["streak"] = 0
    session["opravljeni"] = 0
    session.modified = True
    return jsonify({"ok": True})

if __name__ == "__main__":
    print("\n🎮 ZestQuest strežnik se zaganja...")
    print(f"   Mapa projekta: {BASE_DIR}")
    print("   Odpri: http://localhost:5000\n")
    app.run(debug=True, port=5000)
