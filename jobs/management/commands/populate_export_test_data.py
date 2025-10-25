"""
Django management command to populate test data for CSV export testing.
Run with: python manage.py populate_export_test_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
import random

from jobs.models import Job, JobApplication, EmailCommunication
from profiles.models import (
    Profile, Skill, ProfileSkill, Education, WorkExperience, 
    Link, UserProfile, ProfilePrivacySettings
)
from kanban.models import PipelineStage, KanbanBoard, ProfileCard, ProfileLike


class Command(BaseCommand):
    help = 'Populate database with test data for CSV export testing'

    def __init__(self):
        super().__init__()
        self.test_users = []
        self.test_recruiters = []
        self.test_job_seekers = []
        self.test_jobs = []
        self.test_profiles = []
        self.test_skills = []

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to populate test data...'))
        
        # Create test data
        self.create_skills()
        self.create_recruiters()
        self.create_job_seekers()
        self.create_jobs()
        self.create_applications()
        self.create_email_communications()
        self.create_kanban_data()
        self.create_profile_likes()
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ TEST DATA CREATED SUCCESSFULLY!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'\n📊 Summary:'))
        self.stdout.write(self.style.SUCCESS(f'  • Recruiters: {len(self.test_recruiters)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Job Seekers: {len(self.test_job_seekers)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Jobs: {len(self.test_jobs)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Applications: {JobApplication.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  • Skills: {len(self.test_skills)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Email Communications: {EmailCommunication.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  • Pipeline Cards: {ProfileCard.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  • Profile Likes: {ProfileLike.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('\n🎯 You can now test CSV exports in the admin panel!'))
        self.stdout.write(self.style.SUCCESS('🗑️  When done, run: python manage.py cleanup_export_test_data\n'))

    def create_skills(self):
        """Create common skills"""
        self.stdout.write('Creating skills...')
        skill_names = [
            'Python', 'JavaScript', 'React', 'Django', 'Node.js',
            'SQL', 'MongoDB', 'AWS', 'Docker', 'Kubernetes',
            'Product Management', 'Agile', 'Scrum', 'UI/UX Design',
            'Figma', 'Adobe XD', 'Leadership', 'Communication',
            'Project Management', 'Data Analysis'
        ]
        
        for skill_name in skill_names:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            self.test_skills.append(skill)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(self.test_skills)} skills'))

    def create_recruiters(self):
        """Create test recruiters"""
        self.stdout.write('Creating recruiters...')
        recruiter_data = [
            {'username': 'test_recruiter1', 'first_name': 'Alice', 'last_name': 'Wong', 'email': 'alice.wong@sokka-test.com'},
            {'username': 'test_recruiter2', 'first_name': 'Bob', 'last_name': 'Wilson', 'email': 'bob.wilson@sokka-test.com'},
            {'username': 'test_recruiter3', 'first_name': 'Carol', 'last_name': 'Martinez', 'email': 'carol.martinez@sokka-test.com'},
        ]
        
        # Get or create Recruiter group
        recruiter_group, _ = Group.objects.get_or_create(name='Recruiter')
        
        for data in recruiter_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'is_staff': False,
                    'is_active': True
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            
            user.groups.add(recruiter_group)
            
            # Create UserProfile
            user_profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'user_type': 'recruiter'}
            )
            
            self.test_recruiters.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(self.test_recruiters)} recruiters'))

    def create_job_seekers(self):
        """Create test job seekers with profiles"""
        self.stdout.write('Creating job seekers...')
        job_seeker_data = [
            {
                'username': 'test_seeker1',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'headline': 'Senior Full Stack Developer',
                'bio': 'Experienced software engineer with 5+ years building scalable web applications. Passionate about clean code and user experience.',
                'location': 'San Francisco, CA',
                'phone': '415-555-0101'
            },
            {
                'username': 'test_seeker2',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@example.com',
                'headline': 'Product Manager',
                'bio': 'Strategic product leader with expertise in SaaS and mobile products. 7+ years driving product vision and execution.',
                'location': 'New York, NY',
                'phone': '212-555-0102'
            },
            {
                'username': 'test_seeker3',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'email': 'mike.johnson@example.com',
                'headline': 'UX/UI Designer',
                'bio': 'Creative designer focused on creating intuitive and delightful user experiences. 4 years in tech startups.',
                'location': 'Austin, TX',
                'phone': '512-555-0103'
            },
            {
                'username': 'test_seeker4',
                'first_name': 'Sarah',
                'last_name': 'Chen',
                'email': 'sarah.chen@example.com',
                'headline': 'Data Scientist',
                'bio': 'ML engineer specializing in NLP and computer vision. PhD in Computer Science.',
                'location': 'Seattle, WA',
                'phone': '206-555-0104'
            },
            {
                'username': 'test_seeker5',
                'first_name': 'David',
                'last_name': 'Brown',
                'email': 'david.brown@example.com',
                'headline': 'DevOps Engineer',
                'bio': 'Infrastructure expert with deep knowledge of cloud platforms and CI/CD pipelines.',
                'location': 'Boston, MA',
                'phone': '617-555-0105'
            },
        ]
        
        for data in job_seeker_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'is_staff': False,
                    'is_active': True
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            
            # Create UserProfile
            user_profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'user_type': 'job_seeker'}
            )
            
            # Create Profile
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'headline': data['headline'],
                    'bio': data['bio'],
                    'location': data['location'],
                    'phone': data['phone']
                }
            )
            
            # Add skills
            self._add_profile_skills(profile, data['headline'])
            
            # Add work experience
            self._add_work_experience(profile)
            
            # Add education
            self._add_education(profile)
            
            # Add links
            self._add_links(profile)
            
            # Create privacy settings
            ProfilePrivacySettings.objects.get_or_create(
                profile=profile,
                defaults={
                    'profile_visibility': random.choice(['public', 'selective']),
                    'allow_contact': True
                }
            )
            
            self.test_job_seekers.append(user)
            self.test_profiles.append(profile)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(self.test_job_seekers)} job seekers with profiles'))

    def _add_profile_skills(self, profile, headline):
        """Add relevant skills based on headline"""
        skill_mapping = {
            'Developer': ['Python', 'JavaScript', 'React', 'Django', 'SQL', 'Docker'],
            'Product Manager': ['Product Management', 'Agile', 'Scrum', 'Communication', 'Leadership'],
            'Designer': ['UI/UX Design', 'Figma', 'Adobe XD', 'Communication'],
            'Data Scientist': ['Python', 'SQL', 'Data Analysis', 'MongoDB'],
            'DevOps': ['Docker', 'Kubernetes', 'AWS', 'Python', 'SQL']
        }
        
        # Find matching skills
        skills_to_add = []
        for key, skills in skill_mapping.items():
            if key.lower() in headline.lower():
                skills_to_add = skills
                break
        
        # Add skills with random proficiency
        proficiency_levels = ['intermediate', 'advanced', 'expert']
        for skill_name in skills_to_add[:5]:  # Max 5 skills
            skill = Skill.objects.get(name=skill_name)
            ProfileSkill.objects.get_or_create(
                profile=profile,
                skill=skill,
                defaults={'proficiency_level': random.choice(proficiency_levels)}
            )

    def _add_work_experience(self, profile):
        """Add work experience"""
        companies = ['Tech Corp', 'StartupXYZ', 'Innovation Labs', 'Digital Solutions']
        positions = ['Senior Engineer', 'Engineer', 'Lead Developer', 'Consultant', 'Specialist']
        
        num_experiences = random.randint(2, 3)
        current_date = timezone.now().date()
        
        for i in range(num_experiences):
            is_current = (i == 0)
            years_ago_start = i * 2 + 1
            years_ago_end = i * 2 if not is_current else None
            
            WorkExperience.objects.get_or_create(
                profile=profile,
                company=random.choice(companies),
                position=random.choice(positions),
                defaults={
                    'start_date': current_date - timedelta(days=years_ago_start * 365),
                    'end_date': None if is_current else current_date - timedelta(days=years_ago_end * 365),
                    'is_current': is_current,
                    'description': 'Led development of key features and mentored junior team members. Improved system performance by 40%.',
                    'location': profile.location
                }
            )

    def _add_education(self, profile):
        """Add education"""
        universities = ['MIT', 'Stanford University', 'UC Berkeley', 'Harvard University', 'Carnegie Mellon']
        degrees = ['Bachelor of Science', 'Master of Science', 'PhD']
        fields = ['Computer Science', 'Software Engineering', 'Information Systems', 'Data Science']
        
        current_date = timezone.now().date()
        
        Education.objects.get_or_create(
            profile=profile,
            institution=random.choice(universities),
            degree=random.choice(degrees),
            field_of_study=random.choice(fields),
            defaults={
                'start_date': current_date - timedelta(days=8 * 365),
                'end_date': current_date - timedelta(days=4 * 365),
                'gpa': round(random.uniform(3.5, 4.0), 2),
                'is_current': False,
                'description': 'Focused on algorithms, data structures, and software architecture.'
            }
        )

    def _add_links(self, profile):
        """Add social links"""
        username = profile.user.username if profile.user else profile.first_name.lower()
        
        links_data = [
            ('linkedin', f'https://linkedin.com/in/{username}', 'LinkedIn Profile'),
            ('github', f'https://github.com/{username}', 'GitHub Profile'),
            ('portfolio', f'https://{username}.dev', 'Personal Portfolio'),
        ]
        
        for link_type, url, title in links_data:
            Link.objects.get_or_create(
                profile=profile,
                link_type=link_type,
                defaults={'url': url, 'title': title}
            )

    def create_jobs(self):
        """Create test jobs"""
        self.stdout.write('Creating jobs...')
        job_data = [
            {
                'title': 'Senior Full Stack Developer',
                'description': 'We are looking for an experienced Full Stack Developer to join our team. You will work on building scalable web applications using modern technologies.',
                'skills': 'Python, JavaScript, React, Django, SQL, Docker',
                'location': 'San Francisco, CA',
                'salary_min': 120000,
                'salary_max': 180000,
                'is_remote': True,
                'visa_sponsorship': True,
            },
            {
                'title': 'Product Manager',
                'description': 'Lead product strategy and execution for our flagship SaaS product. Work with engineering, design, and business teams.',
                'skills': 'Product Management, Agile, Communication, Leadership',
                'location': 'New York, NY',
                'salary_min': 130000,
                'salary_max': 170000,
                'is_remote': False,
                'visa_sponsorship': False,
            },
            {
                'title': 'UX/UI Designer',
                'description': 'Create beautiful and intuitive user experiences for our mobile and web applications.',
                'skills': 'UI/UX Design, Figma, Adobe XD, User Research',
                'location': 'Austin, TX',
                'salary_min': 90000,
                'salary_max': 130000,
                'is_remote': True,
                'visa_sponsorship': False,
            },
            {
                'title': 'DevOps Engineer',
                'description': 'Build and maintain our cloud infrastructure and CI/CD pipelines. Ensure high availability and scalability.',
                'skills': 'Docker, Kubernetes, AWS, Python, Linux',
                'location': 'Seattle, WA',
                'salary_min': 110000,
                'salary_max': 160000,
                'is_remote': True,
                'visa_sponsorship': True,
            },
            {
                'title': 'Data Scientist',
                'description': 'Develop machine learning models and analyze data to drive business decisions.',
                'skills': 'Python, SQL, Machine Learning, Data Analysis',
                'location': 'Boston, MA',
                'salary_min': 125000,
                'salary_max': 175000,
                'is_remote': False,
                'visa_sponsorship': True,
            },
        ]
        
        for i, data in enumerate(job_data):
            # Vary creation dates
            days_ago = random.randint(5, 30)
            
            job = Job.objects.create(
                title=data['title'],
                description=data['description'],
                skills=data['skills'],
                location=data['location'],
                salary_min=data['salary_min'],
                salary_max=data['salary_max'],
                is_remote=data['is_remote'],
                visa_sponsorship=data['visa_sponsorship'],
                posted_by=self.test_recruiters[i % len(self.test_recruiters)],
                is_active=True
            )
            
            # Manually set created_at to vary dates
            job.created_at = timezone.now() - timedelta(days=days_ago)
            job.save()
            
            self.test_jobs.append(job)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(self.test_jobs)} jobs'))

    def create_applications(self):
        """Create job applications"""
        self.stdout.write('Creating job applications...')
        
        notes = [
            "I'm excited about this opportunity. My experience with Python and Django aligns perfectly with your requirements.",
            "I've been following your company for years and would love to contribute to your mission.",
            "My background in scalable systems and my passion for clean code make me a great fit for this role.",
            "I'm particularly interested in the technical challenges mentioned in the job description.",
            "Looking forward to discussing how my skills can contribute to your team's success."
        ]
        
        count = 0
        # Each job gets 3-5 applications
        for job in self.test_jobs:
            num_apps = random.randint(3, 5)
            applicants = random.sample(self.test_job_seekers, min(num_apps, len(self.test_job_seekers)))
            
            for i, applicant in enumerate(applicants):
                days_ago = random.randint(1, 20)
                
                app = JobApplication.objects.create(
                    job=job,
                    applicant=applicant,
                    tailored_note=random.choice(notes),
                    status=random.choice(['applied', 'review', 'interview', 'offer'])
                )
                
                # Vary application dates
                app.applied_at = timezone.now() - timedelta(days=days_ago)
                app.save()
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} job applications'))

    def create_email_communications(self):
        """Create email communications"""
        self.stdout.write('Creating email communications...')
        
        subjects = [
            "Regarding your application to {job}",
            "Next steps for {job} position",
            "Interview invitation for {job}",
            "Follow-up on your application",
            "Additional questions about your experience"
        ]
        
        messages = [
            "Thank you for applying to our {job} position. We've reviewed your application and would like to schedule an interview. Are you available next week?",
            "We were impressed with your background. Could you provide more details about your experience with {skill}?",
            "Your application stood out among many qualified candidates. We'd love to discuss this opportunity further with you.",
            "Thank you for your interest in joining our team. We're moving forward with your application to the next round.",
            "We appreciate you taking the time to apply. Could you share some examples of your previous work?"
        ]
        
        applications = JobApplication.objects.all()
        count = 0
        
        for app in applications[:15]:  # Create emails for first 15 applications
            recruiter = app.job.posted_by
            days_ago = random.randint(1, 10)
            
            subject = random.choice(subjects).format(job=app.job.title)
            message = random.choice(messages).format(
                job=app.job.title,
                skill=app.job.skills.split(',')[0] if app.job.skills else 'technology'
            )
            
            email = EmailCommunication.objects.create(
                job_application=app,
                sender=recruiter,
                recipient_email=app.applicant.email,
                subject=subject,
                message=message,
                is_read=random.choice([True, False])
            )
            
            email.sent_at = timezone.now() - timedelta(days=days_ago)
            if email.is_read:
                email.read_at = email.sent_at + timedelta(hours=random.randint(1, 48))
            email.save()
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} email communications'))

    def create_kanban_data(self):
        """Create kanban boards and pipeline data"""
        self.stdout.write('Creating kanban/pipeline data...')
        
        # Ensure pipeline stages exist
        stages_data = [
            ('profile_interest', 0, '#3498db'),
            ('resume_review', 1, '#f39c12'),
            ('interview', 2, '#9b59b6'),
            ('hired', 3, '#27ae60'),
            ('rejected', 4, '#e74c3c'),
        ]
        
        stages = {}
        for name, order, color in stages_data:
            stage, _ = PipelineStage.objects.get_or_create(
                name=name,
                defaults={'order': order, 'color': color}
            )
            stages[name] = stage
        
        # Create kanban boards for recruiters
        boards = []
        for recruiter in self.test_recruiters:
            board, _ = KanbanBoard.objects.get_or_create(
                recruiter=recruiter,
                defaults={'name': f"{recruiter.first_name}'s Hiring Pipeline"}
            )
            boards.append(board)
        
        # Add applications to pipeline
        applications = JobApplication.objects.all()
        card_count = 0
        
        for app in applications:
            # Find recruiter's board
            board = KanbanBoard.objects.filter(recruiter=app.job.posted_by).first()
            if board:
                # Map application status to pipeline stage
                status_to_stage = {
                    'applied': 'profile_interest',
                    'review': 'resume_review',
                    'interview': 'interview',
                    'offer': 'hired',
                    'closed': 'rejected'
                }
                
                stage_name = status_to_stage.get(app.status, 'profile_interest')
                stage = stages[stage_name]
                
                profile = Profile.objects.filter(user=app.applicant).first()
                if profile:
                    card, created = ProfileCard.objects.get_or_create(
                        board=board,
                        profile=profile,
                        job_application=app,
                        defaults={
                            'stage': stage,
                            'position': card_count,
                            'notes': f'Strong candidate for {app.job.title}. {random.choice(["Good technical skills.", "Great communication.", "Impressive portfolio.", "Solid experience."])}'
                        }
                    )
                    
                    # Link card to application
                    if created:
                        app.kanban_card = card
                        app.save()
                        card_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(boards)} kanban boards and {card_count} profile cards'))

    def create_profile_likes(self):
        """Create profile likes"""
        self.stdout.write('Creating profile likes...')
        
        count = 0
        for recruiter in self.test_recruiters:
            # Each recruiter likes 3-5 profiles
            num_likes = random.randint(3, 5)
            profiles = random.sample(self.test_profiles, min(num_likes, len(self.test_profiles)))
            
            for profile in profiles:
                days_ago = random.randint(1, 30)
                
                like, created = ProfileLike.objects.get_or_create(
                    recruiter=recruiter,
                    profile=profile
                )
                
                if created:
                    like.liked_at = timezone.now() - timedelta(days=days_ago)
                    like.save()
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {count} profile likes'))

