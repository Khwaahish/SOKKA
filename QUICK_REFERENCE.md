# 🚀 Quick Reference - CSV Export Testing

## Create Test Data ➕

```bash
cd /Users/ompatel/Desktop/SOKKA/SOKKA
python manage.py populate_export_test_data
```

**Creates:**
- 3 Recruiters
- 5 Job Seekers with full profiles
- 5 Jobs
- 15-25 Applications
- Email communications
- Kanban pipeline data
- Profile likes

---

## Test Exports 📊

1. **Start server:**
   ```bash
   python manage.py runserver
   ```

2. **Open admin:** `http://localhost:8000/admin/`

3. **Navigate → Select → Export → Go!**

**Available Exports:**
- Jobs → Jobs
- Jobs → Job applications
- Jobs → Email communications
- Profiles → Profiles
- Profiles → Profile skills
- Profiles → Work experiences
- Profiles → Educations
- Profiles → User profiles
- Kanban → Profile cards
- Kanban → Pipeline stages
- Kanban → Kanban boards
- Kanban → Profile likes

---

## Cleanup Test Data 🗑️

```bash
python manage.py cleanup_export_test_data
```

**Deletes all test data safely!**

---

## Test User Credentials 🔑

**Password for all test users:** `testpass123`

### Recruiters:
- `test_recruiter1` - Alice Wong
- `test_recruiter2` - Bob Wilson
- `test_recruiter3` - Carol Martinez

### Job Seekers:
- `test_seeker1` - John Doe (Developer)
- `test_seeker2` - Jane Smith (Product Manager)
- `test_seeker3` - Mike Johnson (Designer)
- `test_seeker4` - Sarah Chen (Data Scientist)
- `test_seeker5` - David Brown (DevOps)

---

## Full Workflow ✅

```bash
# 1. Create test data
python manage.py populate_export_test_data

# 2. Test exports in admin panel
python manage.py runserver
# → http://localhost:8000/admin/

# 3. Clean up when done
python manage.py cleanup_export_test_data
```

---

## 📚 More Help

- **Quick Start:** `QUICK_START_EXPORT.md`
- **Full Guide:** `CSV_EXPORT_GUIDE.md`
- **Test Data Details:** `TEST_DATA_GUIDE.md`
- **Implementation:** `IMPLEMENTATION_SUMMARY.md`

---

**That's it! Happy testing! 🎉**

