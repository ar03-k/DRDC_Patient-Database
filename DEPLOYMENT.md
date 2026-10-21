# Website and database setup

## Recommended architecture

- Keep Django as the application backend and use PostgreSQL for patient, visit, staff, and document metadata.
- Store uploaded document bytes in a private S3-compatible object-storage bucket. Django stores the document keys in PostgreSQL and returns signed URLs for authorized users.
- Serve the website over HTTPS from a Django-capable host. A managed PostgreSQL service and private object-storage bucket are recommended for production.
- The current interface is a server-rendered website. It is not yet a native desktop or iOS/Android app. The next app phase should add a secured API and a responsive shared frontend; that frontend can be installed as a desktop PWA and packaged for mobile with Capacitor.

The current local SQLite database remains the default. Changing the database setting does not copy existing records or uploaded files.

## Run locally with PostgreSQL

1. Install Python and Docker Desktop.
2. In PowerShell, from the project directory:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Edit `.env`: set a local-only `DB_PASSWORD`. Change `DB_ENGINE=sqlite` to `DB_ENGINE=postgresql`.
4. Create and activate a virtual environment, then install dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

5. Start PostgreSQL and initialize the schema:

   ```powershell
   docker compose up -d db
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Run the website:

   ```powershell
   python manage.py runserver
   ```

   Open `http://127.0.0.1:8000/` and use **Log in** to access patient pages.

To keep using the existing SQLite database, leave `DB_ENGINE=sqlite` in `.env`; no database migration is needed.

## Preserve existing SQLite records when moving to PostgreSQL

Do this as a planned maintenance operation, with a separate verified backup of `db.sqlite3` and the `media` directory. Never put exports containing patient information in source control or an unprotected sync folder.

1. With `DB_ENGINE=sqlite`, export the patient app's records to a protected temporary location:

   ```powershell
   python manage.py dumpdata patients --indent 2 --output "$env:TEMP\clinic-data.json"
   ```

2. Change `.env` to `DB_ENGINE=postgresql`, start the database, and run migrations:

   ```powershell
   docker compose up -d db
   python manage.py migrate
   ```

3. Import the fixture and create a staff account:

   ```powershell
   python manage.py loaddata "$env:TEMP\clinic-data.json"
   python manage.py createsuperuser
   ```

4. If moving documents to object storage, copy the existing `media\patient_docs` files to the bucket using the provider's secure transfer tool while preserving their relative paths. Configure the bucket settings below before importing/serving records. Compare patient, visit, and document counts and test document access before deleting any old copy.
5. After verification, securely remove the temporary export and retain the original backup according to your clinic's retention policy.

This fixture method covers Django database records; it does not copy the actual file bytes. Keep the old database and media backup until the import and document transfer are verified.

## Configure private object storage

Set these environment variables on the host; do not commit credentials:

- `OBJECT_STORAGE_BUCKET_NAME`: bucket name.
- `OBJECT_STORAGE_REGION`: provider region.
- `OBJECT_STORAGE_ENDPOINT_URL`: optional S3-compatible endpoint (leave blank for AWS S3).

Provide credentials through the host's secret manager or workload identity/IAM role, not source files. With the bucket configured, Django uses signed URLs for private files. Test upload, download, and access after login before moving existing records.

## Production checklist

Before exposing the website publicly:

1. Set `DJANGO_DEBUG=False`, provide a unique `DJANGO_SECRET_KEY`, and configure `DJANGO_ALLOWED_HOSTS` with the site's hostname (hostnames only, no scheme).
2. Set `DJANGO_CSRF_TRUSTED_ORIGINS` to the site's HTTPS origin, for example `https://clinic.example.com`.
3. Use HTTPS, encrypted managed PostgreSQL, encrypted backups, a private document bucket, and host-managed secrets. Set up restore tests and monitoring.
4. Run `python manage.py check --deploy` against the production environment.
5. Create staff accounts with `python manage.py createsuperuser`; do not expose public registration. Patient pages now require a login.
6. Confirm that patient routes, uploaded documents, database backups, application logs, and support workflows are limited to authorized staff. Determine and implement the health-data privacy requirements for the jurisdictions where the clinic operates.

`DEBUG=False` intentionally requires `DJANGO_SECRET_KEY`; the development fallback key is generated only when debug mode is enabled. Secure cookies are enabled when debug mode is off, so production must use HTTPS.

## Desktop and mobile apps

The website can be hosted and opened from desktop and mobile browsers after deployment, but this repository does not yet contain an API, PWA manifest/service worker, or native mobile project. To finish the requested app support:

1. Build authenticated API endpoints for patient, visit, and document workflows; apply staff permissions and avoid exposing private file URLs publicly.
2. Make the shared frontend responsive and establish its login/session or token strategy.
3. Add PWA installation for desktop and package the shared frontend as iOS/Android apps with Capacitor; do not cache patient records or documents offline by default.
4. Build and test with Android tooling. iOS signing and App Store builds require macOS/Xcode and Apple Developer enrollment; store publication also requires the respective developer accounts.

The Windows project environment can prepare the backend and Android-side project, but cannot by itself produce a signed iOS release.
