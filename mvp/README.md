# 🎮 ZestQuest – Spletna aplikacija

## Struktura projekta

```
zestquest/
├── app.py              ← Flask backend (strežnik)
├── model_helper.py     ← Razred za napovedovanje
├── model.pkl           ← Naučen AI model
├── encoders.pkl        ← Encoderji za vhode
├── label_enc.pkl       ← Encoder za kategorije
├── requirements.txt    ← Python odvisnosti
└── templates/
    └── index.html      ← Spletna stran
```

## Namestitev in zagon

### 1. Namesti odvisnosti
```bash
pip install -r requirements.txt
```

### 2. Zagotovi, da so .pkl datoteke v mapi
Če jih nimaš, generiraj model:
```bash
# Iz mape eno stopnjo višje
python generiraj_podatke.py
python treniraj_model.py --model gb

# Premakni .pkl datoteke v zestquest/
cp model.pkl encoders.pkl label_enc.pkl zestquest/
```

### 3. Zaženi strežnik
```bash
cd zestquest
python app.py
```

### 4. Odpri brskalnik
```
http://localhost:5000
```

## API Endpoints

| Metoda | URL | Opis |
|--------|-----|------|
| GET | `/` | Glavna stran |
| POST | `/api/napovej` | AI napoved kategorije + quest |
| POST | `/api/opravi` | Označi quest kot opravljen (+XP) |
| POST | `/api/preskoci` | Preskoči quest |
| POST | `/api/reset` | Ponastavi statistike |

### Primer API klica (JavaScript):
```js
const res = await fetch('/api/napovej', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    razpolozenje: 'dolgcas',
    energija: 'nizka',
    lokacija: 'doma',
    skupina: 'sam',
    cas_razpolozljiv: '15_30min',
    osebnost: 'introvert',
    vreme: 'oblacno',
    cas_dneva: 'vecer',
  })
});
const data = await res.json();
// data.kategorija → 'kreativno'
// data.quest → { naslov, opis, cas, xp }
// data.verjetnosti → { kreativno: 0.87, ... }
```
