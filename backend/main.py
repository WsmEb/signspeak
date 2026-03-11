"""
SignSpeak — Backend API
يستقبل نقاط اليد من MediaPipe ويُعيد اسم الإشارة المكتشفة
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI(title="SignSpeak API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── نماذج البيانات ─────────────────────────────────────────────────────────

class HandData(BaseModel):
    landmarks: list  # 21 نقطة لكل منها x, y, z

class Result(BaseModel):
    sign: str
    confidence: float
    description: str

# ── أوصاف الإشارات ─────────────────────────────────────────────────────────

DESCRIPTIONS = {
    "A": "قبضة مغلقة مع رفع الإبهام للجانب",
    "B": "أربعة أصابع مرفوعة معاً والإبهام مطوي",
    "C": "الأصابع منحنية على شكل حرف C",
    "D": "السبابة مرفوعة والبقية تلمس الإبهام",
    "E": "كل الأصابع منحنية نحو الإبهام",
    "F": "السبابة تلمس الإبهام مع رفع الباقي",
    "G": "السبابة والإبهام أفقيان",
    "H": "السبابة والوسط أفقيان",
    "I": "الخنصر مرفوع وحده",
    "K": "السبابة والوسط مرفوعان والإبهام بينهما",
    "L": "السبابة والإبهام يصنعان شكل L",
    "M": "الإبهام تحت ثلاثة أصابع",
    "N": "الإبهام تحت أصبعين",
    "O": "الأصابع تصنع دائرة مع الإبهام",
    "R": "السبابة والوسط متقاطعان",
    "S": "قبضة مغلقة والإبهام فوقها",
    "T": "الإبهام بين السبابة والوسط",
    "U": "السبابة والوسط مرفوعان ومضمومان",
    "V": "السبابة والوسط مرفوعان شكل V",
    "W": "ثلاثة أصابع مرفوعة",
    "Y": "الإبهام والخنصر مرفوعان",
    "مرحباً": "كل الأصابع مرفوعة — تحية",
    "أحبك": "الإبهام والسبابة والخنصر مرفوعة معاً",
    "شكراً": "اليد تلمس الذقن ثم تتحرك للأمام",
    "نعم": "قبضة تهتز للأعلى والأسفل",
    "لا": "السبابة تتحرك يميناً ويساراً",
    "توقف": "كل الأصابع مرفوعة وباليد للأمام",
    "ساعدني": "يد مفتوحة ترفع الأخرى",
}

# ── خوارزمية التصنيف ───────────────────────────────────────────────────────

def fingers_state(pts):
    """
    تُحدد أي الأصابع مرفوعة
    تُعيد [إبهام، سبابة، وسط، بنصر، خنصر]
    """
    tips  = [4, 8, 12, 16, 20]
    pips  = [3, 6, 10, 14, 18]
    mcps  = [2, 5,  9, 13, 17]

    up = []
    # الإبهام — يُقاس أفقياً
    up.append(pts[4]["x"] > pts[3]["x"])
    # بقية الأصابع — يُقاس رأسياً
    for tip, pip in zip(tips[1:], pips[1:]):
        up.append(pts[tip]["y"] < pts[pip]["y"])
    return up

def classify(landmarks):
    pts = landmarks
    up = fingers_state(pts)
    th, ix, mx, rx, pk = up
    n = sum(up)

    # ── إشارات الحروف ──────────────────────────────────
    if up == [False, False, False, False, False]:
        return "A", 0.85
    if up == [False, True, True, True, True]:
        return "B", 0.87
    if up == [False, True, False, False, False]:
        return "D", 0.82
    if up == [False, True, True, False, False]:
        return "V", 0.88
    if up == [True, True, False, False, False]:
        return "L", 0.86
    if up == [False, False, False, False, True]:
        return "I", 0.83
    if up == [True, False, False, False, True]:
        return "أحبك", 0.93
    if up == [True, True, True, True, True]:
        return "مرحباً", 0.91
    if up == [True, False, False, False, False]:
        return "Y", 0.79
    if up == [False, True, True, True, False]:
        return "W", 0.81
    if up == [False, True, True, False, False] and \
       abs(pts[8]["x"] - pts[12]["x"]) < 0.04:
        return "U", 0.80
    if up == [True, True, True, False, False]:
        return "K", 0.77
    if up == [False, False, True, False, False]:
        return "M", 0.74
    if up == [True, True, True, True, False]:
        return "توقف", 0.85

    # ── تصنيف عام بعدد الأصابع ─────────────────────────
    fallback = {0: ("S", 0.65), 1: ("G", 0.60), 2: ("R", 0.60),
                3: ("F", 0.58), 4: ("O", 0.58), 5: ("مرحباً", 0.70)}
    return fallback.get(n, ("?", 0.40))

# ── نقاط الـ API ───────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "SignSpeak API تعمل", "version": "1.0"}

@app.post("/predict", response_model=Result)
def predict(data: HandData):
    if not data.landmarks or len(data.landmarks) < 21:
        return Result(sign="?", confidence=0.0, description="لم يتم الكشف عن يد")

    sign, conf = classify(data.landmarks)
    desc = DESCRIPTIONS.get(sign, f"الإشارة: {sign}")
    return Result(sign=sign, confidence=round(conf, 2), description=desc)

@app.get("/signs")
def all_signs():
    return {"total": len(DESCRIPTIONS), "signs": DESCRIPTIONS}
