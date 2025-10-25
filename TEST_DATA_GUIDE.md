# Test Data Guide for CSV Export Testing

## Quick Start

### Step 1: Populate Test Data

Run this command to create comprehensive test data:

```bash
cd /Users/ompatel/Desktop/SOKKA/SOKKA
python manage.py populate_export_test_data
```

**What this creates:**
- ✅ 3 Recruiters (with login credentials)
- ✅ 5 Job Seekers with complete profiles
- ✅ 5 Jobs (various positions)
- ✅ 15-25 Job Applications
- ✅ 20+ Skills
- ✅ 10-15 Work Experience records
- ✅ 5+ Education records
- ✅ Email Communications
- ✅ Kanban Boards & Pipeline Cards
- ✅ Profile Likes

---

### Step 2: Test CSV Exports

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Go to admin panel:**
   ```
   http://localhost:8000/admin/
   ```

3. **Test any export:**
   - Navigate to any model (e.g., Jobs → Job applications)
   - Select items
   - Choose "Export to CSV" action
   - Click "Go"

---

### Step 3: Cleanup When Done

**Option A: With confirmation prompt**
```bash
python manage.py cleanup_export_test_data
```
You'll be asked to confirm before deletion.

**Option B: Skip confirmation (use with caution!)**
```bash
python manage.py cleanup_export_test_data --confirm
```

---

## Test Data Details

### 👥 Test Users Created

#### Recruiters (3 users)
| Username | Name | Email | Password |
|----------|------|-------|----------|
| test_recruiter1 | Alice Wong | alice.wong@sokka-test.com | testpass123 |
| test_recruiter2 | Bob Wilson | bob.wilson@sokka-test.com | testpass123 |
| test_recruiter3 | Carol Martinez | carol.martinez@sokka-test.com | testpass123 |

#### Job Seekers (5 users)
| Username | Name | Email | Role | Password |
|----------|------|-------|------|----------|
| test_seeker1 | John Doe | john.doe@example.com | Senior Full Stack Developer | testpass123 |
| test_seeker2 | Jane Smith | jane.smith@example.com | Product Manager | testpass123 |
| test_seeker3 | Mike Johnson | mike.johnson@example.com | UX/UI Designer | testpass123 |
| test_seeker4 | Sarah Chen | sarah.chen@example.com | Data Scientist | testpass123 |
| test_seeker5 | David Brown | david.brown@example.com | DevOps Engineer | testpass123 |

### 💼 Test Jobs Created

1. **Senior Full Stack Developer** (San Francisco, CA) - Remote, Visa Sponsorship
2. **Product Manager** (New York, NY) - On-site
3. **UX/UI Designer** (Austin, TX) - Remote
4. **DevOps Engineer** (Seattle, WA) - Remote, Visa Sponsorship
5. **Data Scientist** (Boston, MA) - On-site, Visa Sponsorship

Each job includes:
- Detailed description
- Required skills
- Salary range ($90k-$180k)
- Multiple applications (3-5 per job)

### 📊 What You Can Test

#### 1. Job Applications Export
- Filter by status (applied, review, interview, offer)
- Filter by date range
- See calculated fields (days since application)
- View pipeline stages

#### 2. Jobs Export
- Active/inactive jobs
- Remote vs on-site
- Salary ranges
- Application counts

#### 3. Email Communications Export
- Read/unread status
- Response times
- Recruiter activity

#### 4. Profiles Export
- Skills inventory
- Experience calculations
- Privacy settings
- Contact preferences

#### 5. Skills Analysis Export
- Skills distribution
- Proficiency levels
- Experience correlation

#### 6. Work Experience Export
- Career progression
- Duration calculations
- Company distribution

#### 7. Education Export
- Degrees and fields
- GPA information
- Institution analysis

#### 8. Pipeline Candidates Export
- Stage distribution
- Time in each stage
- Conversion metrics

#### 9. Pipeline Stages Export
- Average time per stage
- Candidate counts
- Bottleneck identification

#### 10. Kanban Boards Export
- Recruiter workload
- Hiring success rates
- Board metrics

#### 11. Profile Likes Export
- Recruiter interest patterns
- Candidate attractiveness

#### 12. User Profiles Export
- User activity
- Last login tracking
- User type distribution

---

## Testing Workflow Example

### Example 1: Test Complete Hiring Pipeline

```bash
# 1. Create test data
python manage.py populate_export_test_data

# 2. Start server
python manage.py runserver

# 3. In admin panel, test these exports:
#    - Jobs → Export all jobs
#    - Job applications → Export all applications
#    - Kanban → Profile cards → Export all pipeline candidates
#    - Jobs → Email communications → Export all emails

# 4. Open CSV files in Excel/Google Sheets
#    - Analyze application flow
#    - Check time-to-hire metrics
#    - Review communication patterns

# 5. Clean up when done
python manage.py cleanup_export_test_data
```

### Example 2: Test Skills Gap Analysis

```bash
# 1. Create test data
python manage.py populate_export_test_data

# 2. Export data:
#    - Profiles → Profile skills → Export all
#    - Jobs → Jobs → Export all

# 3. Compare:
#    - Skills.csv shows what candidates have
#    - Jobs.csv shows what's required
#    - Identify gaps

# 4. Clean up
python manage.py cleanup_export_test_data
```

---

## Data Relationships

The test data creates realistic relationships:

```
Users (Recruiters & Job Seekers)
    ↓
Jobs (posted by Recruiters)
    ↓
Job Applications (Job Seekers apply to Jobs)
    ↓
Email Communications (Recruiters contact Applicants)
    ↓
Pipeline Cards (Applications tracked in Kanban)
    ↓
Profile Likes (Recruiters like Candidates)
```

All data includes:
- ✅ Realistic dates (varied over past 30 days)
- ✅ Meaningful content (not just "test test test")
- ✅ Proper status progression (applied → review → interview)
- ✅ Calculated fields (days, durations, counts)
- ✅ Related data (applications link to profiles, jobs, emails)

---

## Safety Features

### ✅ Safe to Run Multiple Times
If you run `populate_export_test_data` multiple times, it won't create duplicates (uses `get_or_create`).

### ✅ Only Deletes Test Data
The cleanup command only deletes users with `test_` prefix and their related data. Your real data is safe!

### ✅ Confirmation Prompt
By default, cleanup asks for confirmation before deleting anything.

### ✅ Detailed Logging
Both commands show exactly what they're creating/deleting.

---

## Troubleshooting

### Problem: Command not found
**Solution:** Make sure you're in the correct directory:
```bash
cd /Users/ompatel/Desktop/SOKKA/SOKKA
python manage.py populate_export_test_data
```

### Problem: Migration errors
**Solution:** Run migrations first:
```bash
python manage.py migrate
```

### Problem: Permission denied
**Solution:** Make sure you're using the right Python environment (virtual environment if you created one).

### Problem: Some data not created
**Solution:** Check terminal output for error messages. Common issues:
- Pipeline stages not initialized
- Skills not created
- Database connection issues

### Problem: Can't login with test users
**Solution:** 
- All test users have password: `testpass123`
- Username format: `test_recruiter1`, `test_seeker1`, etc.

---

## Advanced Usage

### Create More Test Data

Edit the command file to increase quantities:
```python
# In populate_export_test_data.py
num_apps = random.randint(5, 10)  # Increase from (3, 5)
```

### Keep Specific Test Data

To cleanup selectively, modify the cleanup command:
```python
# Remove specific filters in cleanup_export_test_data.py
test_users = User.objects.filter(username='specific_test_user')
```

### Export All at Once

Create a bash script:
```bash
#!/bin/bash
# export_all.sh

echo "Exporting all data..."
# Use Django shell or create custom management command
python manage.py dumpdata > all_data.json
echo "Done!"
```

---

## Pro Tips

### Tip 1: Use Filters Before Exporting
- Date filters: "Past 7 days", "This month"
- Status filters: "Applied", "Interview"
- This simulates real-world usage

### Tip 2: Test Different Scenarios
- Export everything (select all)
- Export filtered subset
- Export single items
- Export with date ranges

### Tip 3: Verify Calculated Fields
- Check "Days Since Application" is accurate
- Verify "Total Experience" calculations
- Confirm "Days in Stage" makes sense

### Tip 4: Test in Excel/Google Sheets
- Open exported CSVs
- Create pivot tables
- Verify data imports correctly
- Check for any encoding issues

### Tip 5: Test Multiple Times
- Create data → Export → Cleanup
- Repeat to ensure consistency
- Verify cleanup removes everything

---

## Quick Reference

### Create Test Data
```bash
python manage.py populate_export_test_data
```

### View Created Data
```bash
# Count test users
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username__startswith='test_').count()

# Count applications
>>> from jobs.models import JobApplication
>>> JobApplication.objects.count()
```

### Cleanup Test Data
```bash
# With confirmation
python manage.py cleanup_export_test_data

# Skip confirmation
python manage.py cleanup_export_test_data --confirm
```

---

## Need More Help?

1. Check command output for detailed logs
2. Review Django admin for data
3. Check terminal for error messages
4. Verify database migrations are up to date

---

**Happy Testing! 🚀**

*Last Updated: October 25, 2025*

