# Innerscript

<p align="center">
  <img src="img/logo.avif" alt="Innerscript Homepage" width="200" style="border-radius:50%">
</p>

Innerscript is a youth mental health community platform. It turns brain science research into practical tools, workshops, and peer support that young people can actually use.

The platform gives people a safe space to share experiences, read evidence-based mental health resources, and talk with others who understand.


## Mission

Mental health support should be accessible, practical, and grounded in science.

Innerscript works to close the gap between neuroscience research and everyday life through:

- Brain science education
- Evidence-based mental health toolkits
- Peer support communities
- School workshops and awareness programs


## Features

### Authentication

- Google OAuth login and email signup
- Email verification
- Django sessions
- Privacy-focused handling of user data

### Community

Users can share personal experiences, write posts and discussions, reply to others, and like content. Each post can carry an image (UUID filename, 5 MB cap, extension whitelist). Every user keeps a profile with a bio, avatar, and role.

### Community ranking

Posts carry a Community Score. It is a heuristic on the likes to comments ratio of a post, not sentiment analysis. It sets the default feed order.

The feed supports three sort modes through `?sort=`:

1. `score` ranks by Community Score
2. `recent` shows newest first
3. `discussed` shows the most commented threads

Posts come in three kinds (blog, discussion, resource) and can be filed under categories. The point is to surface well discussed conversations instead of raw popularity.

### Mental health resources

Anxiety coping strategies, journaling techniques, breathing exercises, stress management, and general mental health education.

### Privacy

Innerscript collects only a name or username and an email address. It does not store Google profile photos, OAuth tokens, location data, ad trackers, or third-party analytics. Users can view their data, edit their profile, and delete their account permanently.


## Requirements

Runtime dependencies are pinned in `requirements.txt`:

- Django 6.0 and django-allauth for auth
- Pillow for image handling
- django-csp and django-axes for security
- djangorestframework
- gunicorn and whitenoise for serving
- psycopg2-binary and dj-database-url for Postgres
- python-dotenv for `.env` loading


## Install

You need Python 3.12 and a `.env` file at the repo root. Set `DJANGO_SECRET_KEY` at a minimum. For local dev set `DJANGO_DEBUG=1`. Google login needs `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Email verification links print to the console in dev. Swap `EMAIL_BACKEND` to SMTP for production.


## Docker

The `Dockerfile` builds on `python:3.12-slim` and runs as a non-root user. On start it runs migrations, collects static files, and serves through gunicorn on port 8000. WhiteNoise serves the collected assets.

```bash
docker build -t innerscript .
docker run -p 8000:8000 --env-file .env innerscript
```

`DJANGO_SECRET_KEY` must be present in the environment at runtime, since migrate and collectstatic run on container start rather than at build time.


## Community guidelines

Innerscript is built around empathy and respect. It offers peer support and educational resources, but it is **not a replacement for professional mental health care**.

Anyone in a crisis should contact a local emergency service, a trusted adult, or a qualified mental health professional.


## Social media

[Instagram](https://www.instagram.com/innerscript.project?igsh=Y2l5ODJmYnc5Zmtj)


## License

Developed for Innerscript and its mission of improving youth mental health accessibility.
