# 🎨 وایت‌برد اشتراکی Real-Time

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django&logoColor=white)
![Channels](https://img.shields.io/badge/Django_Channels-4.0-092E20)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

وایت‌برد آنلاین چندنفره: هرکی لینک اتاق رو داشته باشه می‌تونه همزمان نقاشی کنه و خط‌های بقیه رو لحظه‌ای ببینه. ساخته شده با **Django + Django Channels + Redis**.

> 🎯 **چرا این پروژه؟** نمایش معماری event-driven واقعی: WebSocket دوسویه، broadcast از طریق Redis channel layer، و persist شدن state — همون چیزهایی که توی سیستم‌های real-time production استفاده می‌شه.

---

## ✨ امکانات

- 🎨 نقاشی همزمان چند کاربر روی یک بورد (موس + لمسی)
- 🌈 انتخاب رنگ و ضخامت قلم
- 🧹 پاک کردن بورد برای همه (broadcast)
- 💾 ذخیره‌ی خودکار خط‌ها در دیتابیس — با رفرش صفحه نقاشی از بین نمی‌ره
- 🔗 هر بورد لینک اشتراک‌گذاری یکتا دارد (`/<slug>/`)
- 📱 ریسپانسیو؛ مختصات نرمال‌شده ذخیره می‌شود تا نقاشی گوشی روی دسکتاپ درست دیده شود

## 🏗 معماری

```
┌──────────────┐   WebSocket (JSON)   ┌──────────────┐   pub/sub    ┌─────────┐
│  مرورگر      │ ◄──────────────────► │   Daphne     │ ◄──────────► │  Redis  │
│  (canvas)    │  /ws/boards/<slug>/  │  + Channels  │  channel     │ channel │
└──────────────┘                      └──────┬───────┘   layer      │  layer  │
                                             │                     └─────────┘
                                             ▼ Django ORM
                                      ┌──────────────┐
                                      │ Room / Stroke│
                                      │ (SQLite/PG)  │
                                      └──────────────┘
```

**جریان یک خط (stroke):**

1. کاربر موس را رها می‌کند → مرورگر یک پیام JSON می‌فرستد: `{"type": "stroke", "stroke": {...}}`
2. `WhiteboardConsumer` پیام را اعتبارسنجی و در دیتابیس ذخیره می‌کند
3. از طریق **Redis channel layer** به group اتاق broadcast می‌شود (حتی بین چند process/worker)
4. همه‌ی مرورگرهای وصل به اتاق خط را روی canvas می‌کشند
5. کاربری که تازه وصل می‌شود، اول کل تاریخچه‌ی بورد (`history`) را می‌گیرد

نکته‌ی فنی: مختصات نقاط به‌صورت نرمال‌شده (۰ تا ۱) ذخیره می‌شوند تا روی هر اندازه صفحه درست رندر شوند.

## 🛠 تکنولوژی‌ها

| لایه | تکنولوژی |
|---|---|
| Backend | Django 5, Django Channels 4 |
| Realtime | WebSocket + Redis channel layer (`channels-redis`) |
| ASGI Server | Daphne (چون Gunicorn به‌تنهایی WebSocket ندارد) |
| Database | SQLite (پیش‌فرض) / PostgreSQL |
| Frontend | HTML5 Canvas + Vanilla JS (بدون فریم‌ورک) |
| Deploy | Docker + docker-compose |

## 🚀 اجرا

### با Docker (پیشنهادی)

```bash
cd realtime-whiteboard
docker compose up --build
```

بعد مرورگر را باز کن: **http://localhost:8000**
(صفحه‌ی اول یک اتاق تازه می‌سازد و ریدایرکت می‌کند؛ لینک را برای بقیه بفرست تا همزمان نقاشی کنید.)

### اجرای لوکال (بدون Docker)

```bash
# ۱) Redis را بالا بیاور (مثلاً با Docker)
docker run -d -p 6379:6379 redis:7-alpine

# ۲) محیط پایتون
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# ۳) دیتابیس و اجرا (daphne جایگزین runserver چون WebSocket لازم داریم)
python manage.py migrate
daphne -b 127.0.0.1 -p 8000 whiteboard_project.asgi:application
```

## 🗺 نقشه‌ی راه (Roadmap)

- [ ] صفحه‌ی لیست اتاق‌ها (rooms list)
- [ ] احراز هویت ساده + نام نمایشی کاربران
- [ ] نمایش کاربران آنلاین هر اتاق (presence)
- [ ] خروجی PNG از بورد (export)
- [ ] Undo/Redo
- [ ] PostgreSQL به‌جای SQLite در compose + تست‌ها (pytest)

---

## English Summary

**Realtime collaborative whiteboard** built with Django, Django Channels and Redis.

- Multiple users draw simultaneously on a shared canvas (mouse + touch); strokes broadcast in real time via WebSocket through a Redis channel layer, so it scales across Daphne workers.
- Strokes are persisted (Room/Stroke models) and replayed to newcomers; each room has a unique share link.
- Points are stored normalized (0–1) so drawings render correctly on any screen size.
- Stack: Django 5, Channels 4, channels-redis, Daphne (ASGI — plain Gunicorn can't do WebSockets), SQLite/PostgreSQL, vanilla JS canvas frontend, Docker Compose (web + redis).

**Run:** `docker compose up --build` → open http://localhost:8000

**Roadmap:** rooms list, simple auth + display names, online presence, PNG export, undo/redo, PostgreSQL + pytest.
