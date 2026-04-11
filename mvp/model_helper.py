"""
ZestQuest - Pomočnik za uporabo modela na spletni strani
=========================================================
Naloži model.pkl, encoders.pkl in label_enc.pkl ter
izpostavi enostavno funkcijo za napovedovanje.

Primer (Flask / FastAPI):
    from model_helper import ZestQuestPredictor
    predictor = ZestQuestPredictor()
    rezultat = predictor.napovej({
        "osebnost": "introvert",
        "cas_dneva": "vecer",
        ...
    })
"""

import os
import pickle
import pandas as pd

KATEGORICNE_KOLONE = [
    "osebnost", "cas_dneva", "vreme", "energija",
    "lokacija", "razpolozenje", "skupina", "cas_razpolozljiv"
]
NUMERICNE_KOLONE = ["starost", "xp_skupaj", "streak_dni", "opravljeni_questi"]

# Vse veljavne vrednosti – koristno za validacijo v API-ju
VELJAVNE_VREDNOSTI = {
    "osebnost":         ["introvert", "ekstrovert", "ambivert"],
    "cas_dneva":        ["jutro", "dopoldne", "popoldne", "vecer", "noc"],
    "vreme":            ["soncno", "oblacno", "dezevno", "snezno", "vetrovmo"],
    "energija":         ["nizka", "srednja", "visoka"],
    "lokacija":         ["doma", "v_mestu", "v_naravi", "v_soli", "na_delu"],
    "razpolozenje":     ["dolgcas", "vesel", "utrujen", "motiviran", "stresen", "umirjen"],
    "skupina":          ["sam", "z_enim", "skupina"],
    "cas_razpolozljiv": ["do_5min", "5_15min", "15_30min", "30_60min", "vec_kot_uro"],
}


class ZestQuestPredictor:
    """Razred za napovedovanje kategorije sidequesta."""

    def __init__(self, mapa="."):
        """
        mapa: mapa, kjer se nahajajo model.pkl, encoders.pkl, label_enc.pkl
        """
        self.model     = self._nalozi(os.path.join(mapa, "model.pkl"))
        self.encoders  = self._nalozi(os.path.join(mapa, "encoders.pkl"))
        self.label_enc = self._nalozi(os.path.join(mapa, "label_enc.pkl"))
        print("✅ ZestQuestPredictor naložen.")

    def _nalozi(self, pot):
        if not os.path.exists(pot):
            raise FileNotFoundError(
                f"Datoteka '{pot}' ne obstaja. "
                f"Najprej poženi: python treniraj_model.py"
            )
        with open(pot, "rb") as f:
            return pickle.load(f)

    def validiraj(self, podatki: dict) -> list:
        """Vrne seznam napak v vhodnih podatkih."""
        napake = []
        for kol, veljavne in VELJAVNE_VREDNOSTI.items():
            vrednost = podatki.get(kol)
            if vrednost is None:
                napake.append(f"Manjkajoče polje: '{kol}'")
            elif vrednost not in veljavne:
                napake.append(f"Neveljavna vrednost za '{kol}': '{vrednost}'. Dovoljeno: {veljavne}")
        return napake

    def napovej(self, podatki: dict) -> dict:
        """
        Napove kategorijo sidequesta.

        Vhod (dict):
          osebnost, cas_dneva, vreme, energija, lokacija,
          razpolozenje, skupina, cas_razpolozljiv,
          starost, xp_skupaj, streak_dni, opravljeni_questi

        Izhod (dict):
          kategorija       – napovedana kategorija (str)
          verjetnosti      – dict {kategorija: verjetnost}
          top3             – seznam top 3 kategorij z verjetnostmi
        """
        napake = self.validiraj(podatki)
        if napake:
            raise ValueError("Napake v vhodnih podatkih:\n" + "\n".join(napake))

        # Encodiranje kategoričnih
        vrstica = {}
        for kol in KATEGORICNE_KOLONE:
            vrednost = podatki[kol]
            try:
                vrstica[kol] = self.encoders[kol].transform([vrednost])[0]
            except ValueError:
                # Neznan razred → fallback na 0
                vrstica[kol] = 0

        # Numerične (z defaultnimi vrednostmi)
        vrstica["starost"]          = int(podatki.get("starost", 20))
        vrstica["xp_skupaj"]        = int(podatki.get("xp_skupaj", 0))
        vrstica["streak_dni"]       = int(podatki.get("streak_dni", 0))
        vrstica["opravljeni_questi"] = int(podatki.get("opravljeni_questi", 0))

        X = pd.DataFrame([vrstica])

        # Napoved
        napoved_enc  = self.model.predict(X)[0]
        verjetnosti  = self.model.predict_proba(X)[0]
        razredi      = self.label_enc.classes_

        kategorija   = self.label_enc.inverse_transform([napoved_enc])[0]
        ver_dict     = {r: round(float(v), 4) for r, v in zip(razredi, verjetnosti)}
        top3 = sorted(ver_dict.items(), key=lambda x: -x[1])[:3]

        return {
            "kategorija":  kategorija,
            "verjetnosti": ver_dict,
            "top3":        [{"kategorija": k, "verjetnost": v} for k, v in top3],
        }

    def batch_napovej(self, seznam_podatkov: list) -> list:
        """Napoved za seznam vhodov hkrati."""
        return [self.napovej(p) for p in seznam_podatkov]


# ─── Primer direktne uporabe ───────────────────────────────────────────────────

if __name__ == "__main__":
    predictor = ZestQuestPredictor()

    testni_primeri = [
        {
            "osebnost": "introvert", "cas_dneva": "vecer", "vreme": "dezevno",
            "energija": "nizka", "lokacija": "doma", "razpolozenje": "utrujen",
            "skupina": "sam", "cas_razpolozljiv": "15_30min",
            "starost": 22, "xp_skupaj": 100, "streak_dni": 3, "opravljeni_questi": 10,
        },
        {
            "osebnost": "ekstrovert", "cas_dneva": "dopoldne", "vreme": "soncno",
            "energija": "visoka", "lokacija": "v_naravi", "razpolozenje": "motiviran",
            "skupina": "skupina", "cas_razpolozljiv": "vec_kot_uro",
            "starost": 25, "xp_skupaj": 2000, "streak_dni": 30, "opravljeni_questi": 80,
        },
        {
            "osebnost": "ambivert", "cas_dneva": "popoldne", "vreme": "oblacno",
            "energija": "srednja", "lokacija": "v_mestu", "razpolozenje": "dolgcas",
            "skupina": "z_enim", "cas_razpolozljiv": "30_60min",
            "starost": 19, "xp_skupaj": 450, "streak_dni": 7, "opravljeni_questi": 25,
        },
    ]

    print("\n" + "=" * 50)
    print("  DEMO – ZestQuestPredictor")
    print("=" * 50)

    for i, primer in enumerate(testni_primeri, 1):
        rez = predictor.napovej(primer)
        print(f"\n[Primer {i}]")
        print(f"  Vhod: {primer['razpolozenje']}, {primer['energija']} energija, {primer['lokacija']}")
        print(f"  ➡  Kategorija: {rez['kategorija'].upper()}")
        print("  Top 3:")
        for item in rez["top3"]:
            print(f"     {item['kategorija']:<16} {item['verjetnost']*100:.1f}%")

    print("\n✅ model_helper.py je pripravljen za integracijo v Flask/FastAPI!\n")
