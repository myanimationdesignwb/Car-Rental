# Rohit Transport, Tour and Travels

A Flask-based vehicle rental website for a driver-provided fleet in Ranchi, Muri and Silli, Jharkhand.

## Features
- Premium home page with fleet preview and booking CTA
- Fleet listing and individual vehicle detail pages
- Multi-step ride booking flow
- Booking tracking form
- Contact form and local SEO pages
- WhatsApp notification support with Meta/Twilio/email fallback design
- SQLite fallback for local development, with PostgreSQL support via `DATABASE_URL`

## Local setup
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   . .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment values:
   ```bash
   copy .env.example .env
   ```
   Then update the values in `.env`.
4. Run the app:
   ```bash
   flask --app run run
   ```
   or:
   ```bash
   python run.py
   ```

## Neon PostgreSQL setup
1. Create a Neon project and database.
2. Copy the connection string into `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```
3. Initialize migrations:
   ```bash
   flask --app run db init
   flask --app run db migrate -m "initial migration"
   flask --app run db upgrade
   ```

## Seeding vehicles
```bash
python seed.py
```
This inserts the fleet and default route fare entries used by the site.

## WhatsApp Cloud API setup
1. Create a WhatsApp Business app in Meta.
2. Set `WHATSAPP_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID` in `.env`.
3. Ensure the business phone number is configured as `OWNER_WHATSAPP`.
4. Use a business-initiated approved template for booking notifications.

## Replacing vehicle photos
- Keep each image filename exactly as the database `image_path` expects, for example `ertiga.jpg` under `app/static/images/vehicles/`.
- Replace the generated placeholders with real vehicle photos.
- The app expects a `16:10` ratio and uses lazy loading for performance.

## Deployment
### Render
- Set environment variables in Render dashboard.
- Add a startup command such as:
  ```bash
  gunicorn run:app
  ```

### Railway
- Connect the repository.
- Set `DATABASE_URL`, `SECRET_KEY`, and WhatsApp variables in the project environment.

### VPS
- Use gunicorn + nginx or a reverse proxy.
- Example:
  ```bash
  gunicorn --bind 0.0.0.0:8000 run:app
  ```

## Owner must supply
- Real vehicle photos in the same filenames
- Final price values and route fares for the admin app
- Logo asset replacement if desired
- WhatsApp/Meta credentials and SMTP credentials when live notifications are enabled
