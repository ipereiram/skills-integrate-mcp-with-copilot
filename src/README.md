# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- View registered students without an account
- Manage student registrations after teacher login

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## Teacher access

Teacher credentials are stored in `src/teachers.json` as salted PBKDF2 password
hashes; plain-text passwords are never saved. Generate a record with:

```
python src/create_teacher.py <username>
```

The command prompts for the password and prints a JSON record. Add that record
to the `teachers` array in `src/teachers.json`. Do not commit real teacher
credentials. The app starts with no teacher accounts configured.

After configuration, use **Teacher login** in the page header to sign in.
Teacher sessions are held in memory and expire after 12 hours. For HTTPS
deployments, serve the app over HTTPS so the session cookie is marked secure.

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/auth/login`                                                     | Log in as a teacher                                                 |
| POST   | `/auth/logout`                                                    | Log out the current teacher                                         |
| GET    | `/auth/me`                                                        | Check the current login status                                      |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher-only student registration                                   |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher-only student removal                                      |

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
