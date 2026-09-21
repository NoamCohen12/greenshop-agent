# GreenShop — סוכן שירות לקוחות אוטונומי

מערכת שירות לקוחות מבוססת LangGraph, המשלבת RAG למענה על שאלות ידע ואוטומציית n8n לביצוע פעולות בפועל על הזמנות לקוח.

מסמך האפיון המלא: [`docs/system_specification.pdf`](docs/system_specification.pdf)

---

## הרצה מהירה (Docker)

```bash
# 1. יצירת קובץ ההגדרות
cp .env.example .env
# ערוך את .env והזן מפתח OPENAI_API_KEY (או שנה ל-MODEL_PROVIDER=ollama)

# 2. הפעלת כל המערכת
docker-compose up --build
```

המערכת תעלה על:

| שירות | כתובת |
|---|---|
| שרת הסוכן (Flask) | http://localhost:5000 |
| n8n | http://localhost:5678 |

מסד הנתונים הוקטורי נבנה אוטומטית בהפעלה הראשונה — אין צורך בשלבים ידניים.

### הגדרת ה-Workflow ב-n8n

בהפעלה הראשונה בלבד:

1. פתח את http://localhost:5678 וצור משתמש מקומי.
2. צור workflow חדש → תפריט `⋯` → **Import from File** → בחר [`docs/n8n_workflow.json`](docs/n8n_workflow.json).
3. שמור והפעל (מתג **Active**).

---

## בדיקה

```bash
python -m tests.test_scenarios
```

מריץ שישה תרחישים המכסים את כל מסלולי הגרף: שאלת ידע, בקשה ספציפית ללקוח, ניסיון Prompt Injection, שאלה מחוץ לתחום, ומקרי קצה של הזמנה שאינה קיימת ושל בקשה ללא מספר הזמנה.

### נתוני הדמה

הנתונים מופרדים לשתי שכבות, בהתאם לתפקידן:

**ידע סטטי** (`data/knowledge_base/`) — מדיניות החזרות, מדיניות משלוחים וקטלוג מוצרים. נכנס ל-RAG.

**נתוני לקוח דינמיים** (בתוך `docs/n8n_workflow.json`) — מסד הזמנות מדומה, שאליו הסוכן מגיע רק דרך קריאה לכלי:

| הזמנה | סטטוס | שווי | הערה |
|---|---|---|---|
| `12345` | בדרך אליך | 278 ₪ | פיצוי נחסם בתקרת 200 ₪ |
| `67890` | נמסר | 89 ₪ | פיצוי מוגבל לשווי ההזמנה |
| `55555` | מתעכב במחסן | 129 ₪ | |
| `77777` | נמסר | 149 ₪ | מבצע "כל המכירות סופיות" — לא ניתן להחזרה |
| `99999` | — | — | לא קיים במערכת (מקרה קצה) |

ההזמנות יושבות ב-n8n ולא בבסיס הידע בכוונה: כך הסוכן אינו "יודע" אותן מראש וחייב לקרוא לכלי כדי להשיג אותן.

בדיקה ידנית של ה-API:

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "מה מדיניות ההחזרות שלכם?"}'
```

---

## החלפת ספק המודל

המערכת תומכת בשני ספקים, הנבחרים דרך משתנה הסביבה `MODEL_PROVIDER`:

| ערך | מודל שיחה | מודל Embedding |
|---|---|---|
| `openai` | `gpt-4o-mini` | `text-embedding-3-small` |
| `ollama` | `llama3.2` | `nomic-embed-text` |

**חשוב:** מודלי embedding שונים מייצרים וקטורים במימדים שונים. לאחר החלפת ספק יש לבנות מחדש את המסד הוקטורי:

```bash
rm -rf chroma_db
python -m src.rag.vector_store
```

---

## מבנה הפרויקט

```
├── src/
│   ├── graph.py                  # הגדרת ה-StateGraph והקשתות המותנות
│   ├── state.py                  # מבנה ה-State העובר בין הצמתים
│   ├── model_provider.py         # בחירת ספק המודל (OpenAI / Ollama)
│   ├── server.py                 # שרת Flask ו-API endpoints
│   ├── startup.py                # נקודת כניסה: בניית המסד הוקטורי + הפעלת השרת
│   ├── nodes/                    # חמשת צמתי הגרף
│   ├── tools/n8n_tool.py         # הכלי לקריאת ה-Webhook של n8n
│   └── rag/vector_store.py       # בניית וטעינת מסד הנתונים הוקטורי
├── data/knowledge_base/          # מסמכי המקור ל-RAG
├── docs/                         # אפיון, תרשימים, ו-workflow לייבוא
└── tests/test_scenarios.py       # תרחישי בדיקה
```

---

## הרצה מקומית (ללא Docker)

דורש Python 3.11+ ומופע n8n פעיל.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m src.startup
```
