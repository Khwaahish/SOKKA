## Candidate Search API (User Story 11)

This API lets recruiters search candidates by skills, location radius, and projects, and returns ranked results.

### Quick start
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py loaddata candidates/fixtures/sample_data.json
python manage.py runserver
```

### Search endpoint
- Method: POST
- URL: `/api/candidates/search`
- Body example:
```json
{
  "skills": ["Python", "Django"],
  "requireAllSkills": false,
  "minSkillLevel": 3,
  "projects": ["api"],
  "location": { "lat": 37.7749, "lng": -122.4194, "radiusKm": 100 },
  "page": 1
}
```

### cURL example
```bash
curl -s http://127.0.0.1:8000/api/candidates/search \
  -H "Content-Type: application/json" \
  -d '{"skills":["Python","Django"],"requireAllSkills":false,"minSkillLevel":3,"projects":["api"],"location":{"lat":37.7749,"lng":-122.4194,"radiusKm":100}}' | jq .
```
