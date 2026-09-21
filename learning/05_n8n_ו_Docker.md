# חלק 5 — n8n ו-Docker

---

## 5.1 מה זה n8n

כלי אוטומציה ויזואלי בקוד פתוח. במקום לכתוב קוד שמתחבר למסד נתונים, לשירות שילוח ולמערכת קופונים — גוררים תיבות על מסך ומחברים ביניהן.

### למה הוא בפרויקט

**הדרישה במסמך:** "המערכת חייבת לבצע פעולה משנה מצב (State) בעולם החיצון דרך n8n... ולא רק להציג מידע."

n8n מייצג את **המערכות של החברה** — מסד ההזמנות, חברת השילוח, מערכת הקופונים. זה מה שהופך את GreenShop מצ'אטבוט שמדבר לסוכן שמבצע.

### מודל העבודה

```
הסוכן (Python)                    n8n
     │                             │
     │──── HTTP POST + JSON ──────>│  Webhook מקבל
     │                             │  Switch מנתב
     │                             │  Code מבצע
     │<─── JSON response ──────────│  Respond מחזיר
     │
  ממשיך לנסח תשובה
```

**הפרדת אחריות:** הסוכן לא יודע איך בודקים סטטוס הזמנה. הוא רק יודע לשלוח בקשה ולקבל תשובה. הלוגיקה העסקית יושבת ב-n8n. אם החברה תחליף ספק שילוח — משנים ב-n8n, הסוכן לא נוגע.

---

## 5.2 מבנה ה-Workflow

`docs/n8n_workflow.json`

```
[Webhook]  →  [Switch By Request Type]  →  [Fetch Order Status]   →  [Respond]
                                        ↘  [Create Refund Request] ↗
```

### הצמתים

**1. Webhook** — נקודת הכניסה
- נתיב: `/webhook/greenshop`
- שיטה: POST
- `responseMode: "responseNode"` — לא עונה מיד, ממתין לצומת ה-Respond

**2. Switch By Request Type** — צומת הלוגיקה
```
אם $json.body.request_type == "order_status"   → מוצא 1
אם $json.body.request_type == "refund_request" → מוצא 2
```

זה ה-if/else של n8n. **המסמך דורש במפורש** לפחות צומת לוגיקה אחת מעבר ל-Webhook.

**3a. Fetch Order Status** — שליפת סטטוס
```javascript
const mockOrderDatabase = {
  '12345': { status: 'בדרך אליך', tracking: 'IL998877', order_total_ils: 278, final_sale: false, ... },
  '67890': { status: 'נמסר', order_total_ils: 89, final_sale: false, ... },
  '55555': { status: 'מתעכב במחסן', order_total_ils: 129, final_sale: false, ... },
  '77777': { status: 'נמסר', order_total_ils: 149, final_sale: true, ... }
};

const order = mockOrderDatabase[orderId];

return [{ json: order
  ? { success: true, order_id: orderId, ...order }
  : { success: false, order_id: orderId, error: 'מספר הזמנה לא נמצא במערכת' }
}];
```

**המסמך מאשר במפורש** שימוש בנתוני Mock: "מותר ואף מומלץ להשתמש במודלי AI ליצור... נתוני Mock כדי שהבדיקה תהיה עשירה ומציאותית."

**למה `order_total_ils` ו-`final_sale` נמצאים כאן:** בלעדיהם אי אפשר לאכוף את מדיניות ההחזרות. `order_total_ils` מאפשר לחשב פיצוי שלא עולה על שווי ההזמנה, ו-`final_sale` מסמן מוצר במבצע "כל המכירות סופיות" שאינו ניתן להחזרה. הזמנה `99999` אינה קיימת בכוונה — זהו מקרה הקצה בתרחיש 5.

**3b. Create Refund Request** — רישום החזר
```javascript
const MAX_COMPENSATION_ILS = 200;
const compensation = Math.min(order.order_total_ils, MAX_COMPENSATION_ILS);
const couponCode = 'GS-' + Math.random().toString(36).substring(2, 8).toUpperCase();
```

כאן יושבת שכבת ההגנה השלישית (ראה חלק 3). הפיצוי נגזר משווי ההזמנה, ולא מספר קבוע.

**למה מסד הנתונים מופיע בשני הצמתים:** כל צומת Code ב-n8n רץ בסביבה נפרדת ואינו רואה משתנים של צומת אחר. במערכת אמיתית שני הצמתים היו פונים לאותו מסד נתונים; כאן, בהיעדר מסד אמיתי, הנתונים משוכפלים. **זו חולשה מודעת** — אם תישאל עליה, זו התשובה (ראה גם 6.9, חולשות ושיפורים עתידיים).

**4. Respond to Webhook** — מחזיר את התוצאה לסוכן.

---

## 5.3 Docker — מושגי יסוד

### הבעיה ש-Docker פותר

"אצלי זה עובד." הקוד רץ במחשב שלך עם Python 3.11 וגרסאות ספציפיות של ספריות. אצל הבודק — Python 3.9, ספריות אחרות, ואולי בכלל Mac. הכל נשבר.

### הפתרון

Docker אורז את **הכל** — קוד, Python, ספריות, הגדרות — לחבילה אחת שרצה זהה בכל מקום.

### שלושה מושגים

| מושג | מה זה | אנלוגיה |
|---|---|---|
| **Image** | תבנית קפואה עם הכל בפנים | מתכון |
| **Container** | מופע רץ של Image | העוגה שנאפתה |
| **Volume** | אחסון שנשמר גם כשה-Container נמחק | מקרר |

מ-Image אחד אפשר להריץ הרבה Containers. כשמוחקים Container — כל מה שבתוכו נעלם, **חוץ** ממה שב-Volume.

---

## 5.4 ה-Dockerfile שלנו

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

EXPOSE 5000

CMD ["python", "-m", "src.startup"]
```

**שורה-שורה:**

- **`FROM python:3.11-slim`** — בסיס. `slim` = גרסה מצומצמת, image קטן יותר.
- **`WORKDIR /app`** — תיקיית העבודה בתוך הקונטיינר.
- **`COPY requirements.txt` לפני `COPY src/`** — זו לא שרירותיות. Docker שומר cache לכל שכבה. אם רק הקוד השתנה, ההתקנה הכבדה של הספריות לא רצה מחדש. **זו שאלה שאוהבים לשאול.**
- **`--no-cache-dir`** — לא לשמור קבצי התקנה מיותרים. image קטן יותר.
- **`EXPOSE 5000`** — תיעוד שהאפליקציה מאזינה שם.
- **`CMD`** — הפקודה שרצה בעליית הקונטיינר.

---

## 5.5 docker-compose.yml

```yaml
services:
  greenshop-agent:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    environment:
      - N8N_WEBHOOK_URL=http://n8n:5678/webhook/greenshop
    volumes:
      - ./chroma_db:/app/chroma_db
    depends_on:
      - n8n

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

**`build: .` מול `image: n8nio/n8n`** — את הסוכן שלנו בונים מ-Dockerfile. את n8n מורידים מוכן.

**`ports: "5000:5000"`** — `פורט_במחשב:פורט_בקונטיינר`. בלי זה, הקונטיינר מבודד ולא נגיש.

**`volumes: ./chroma_db:/app/chroma_db`** — התיקייה במחשב ממופה לתיקייה בקונטיינר. המסד הוקטורי שורד הפעלה מחדש.

**`depends_on: n8n`** — סדר העלייה.

---

## 5.6 רשת Docker — הנקודה הכי מבלבלת

```yaml
environment:
  - N8N_WEBHOOK_URL=http://n8n:5678/webhook/greenshop
```

**למה `n8n` ולא `localhost`?**

`localhost` פירושו "המכונה הזו". בתוך קונטיינר, "המכונה הזו" היא **הקונטיינר עצמו** — לא המחשב ולא קונטיינר אחר.

אם הסוכן היה פונה ל-`localhost:5678`, הוא היה מחפש את n8n **בתוך עצמו**. אין שם כלום.

Docker Compose יוצר רשת פנימית שבה **שם השירות הוא שם המארח**. `http://n8n:5678` מגיע לקונטיינר של n8n.

**למה `environment` דורס את `.env`:** ב-`.env` כתוב `localhost` — נכון להרצה מקומית ללא Docker. ב-compose דורסים ל-`n8n`. אותו קובץ `.env` עובד בשני המצבים.

| מאיפה רצים | כתובת n8n |
|---|---|
| Python מקומי | `http://localhost:5678` |
| מתוך קונטיינר | `http://n8n:5678` |

---

## 5.7 הרצה

```bash
docker-compose up --build      # בנייה + הפעלה
docker-compose down            # עצירה
docker ps                      # מה רץ
docker logs <container_name>   # לוגים
```

**מה קורה ב-`up`:**
1. בניית image של הסוכן
2. הורדת image של n8n (פעם ראשונה)
3. יצירת רשת ו-volumes
4. הפעלת n8n, ואחריו הסוכן
5. `startup.py` בודק אם `chroma_db` קיים — אם לא, בונה אותו
6. Flask עולה על 5000

---

## שאלות לבדיקה עצמית

1. למה `COPY requirements.txt` מופיע לפני `COPY src/`?
2. מה ההבדל בין Image ל-Container?
3. הסוכן בקונטיינר פונה ל-`localhost:5678`. מה יקרה ולמה?
4. מה תפקיד ה-Volume של `chroma_db`? מה היה קורה בלעדיו?
5. איזו דרישה במסמך מחייבת את צומת ה-Switch ב-n8n?
6. הבודק מריץ `docker-compose up` על מחשב נקי. תאר מה קורה עד שהמערכת מוכנה.
