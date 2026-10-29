# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Teacher sign-in to register and unregister students
- Public activity and participant browsing
- Hashed teacher passwords and expiring, HttpOnly sessions

## Getting Started

1. From the repository root, install the dependencies:

   ```
   pip install -r ../requirements.txt
   ```

2. Change to the app directory and create a teacher account. The password must
   be at least 12 characters. The credentials are stored in an ignored
   `teachers.json` file with a salted password hash; the plaintext password is
   never written to disk.

   ```
   cd src
   python create_teacher.py
   ```

3. Configure a stable signing secret, then run the application. Without
   `SESSION_SECRET`, a random secret is generated at startup and existing
   sessions become invalid when the server restarts.

   ```bash
   export SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
   uvicorn app:app --reload
   ```

   When serving over HTTPS, also set `SESSION_COOKIE_SECURE=true`. Leave it
   unset for local HTTP development.

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/auth/login`                                                      | Sign in as a teacher; accepts a JSON username and password           |
| GET    | `/auth/me`                                                         | Get the current teacher session status                               |
| POST   | `/auth/logout`                                                     | Sign out and clear the session cookie                                 |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Register a student (teacher sign-in required)                        |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a student (teacher sign-in required)                   |

## Tests

Run the authentication and route-protection tests from the project root:

```
python -m unittest discover -s src -p 'test_*.py' -v
```

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
