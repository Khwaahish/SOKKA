from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profiles.models import UserProfile
from jobs.models import Job
from django.utils import timezone
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create dummy job postings'

    def handle(self, *args, **options):
        # Get a recruiter user (or create one if none exists)
        recruiter_user = None
        try:
            recruiter_user = User.objects.filter(user_profile__user_type='recruiter').first()
            if not recruiter_user:
                # Create a recruiter if none exists
                recruiter_user = User.objects.create_user(
                    username='recruiter_demo',
                    email='recruiter@company.com',
                    password='password123',
                    first_name='Demo',
                    last_name='Recruiter'
                )
                UserProfile.objects.create(user=recruiter_user, user_type='recruiter')
                self.stdout.write(self.style.SUCCESS('Created demo recruiter user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error with recruiter: {e}'))
            return

        # Dummy job postings
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'description': 'We are looking for an experienced Python developer to join our team. You will work on building scalable web applications using Django and modern Python frameworks.',
                'location': 'San Francisco, CA',
                'salary_min': 120000,
                'salary_max': 180000,
                'is_remote': True,
                'skills': 'Python, Django, PostgreSQL, AWS, Git, REST APIs'
            },
            {
                'title': 'Frontend React Developer',
                'description': 'Join our frontend team to build amazing user interfaces using React, TypeScript, and modern web technologies.',
                'location': 'New York, NY',
                'salary_min': 100000,
                'salary_max': 150000,
                'is_remote': False,
                'skills': 'React, TypeScript, JavaScript, HTML, CSS, Git'
            },
            {
                'title': 'Data Scientist',
                'description': 'We need a data scientist to help us extract insights from large datasets using machine learning and statistical analysis.',
                'location': 'Seattle, WA',
                'salary_min': 130000,
                'salary_max': 200000,
                'is_remote': True,
                'skills': 'Python, Machine Learning, SQL, R, AWS, Statistics'
            },
            {
                'title': 'UI/UX Designer',
                'description': 'Create beautiful and intuitive user experiences for our digital products. Work with cross-functional teams to deliver exceptional design solutions.',
                'location': 'Austin, TX',
                'salary_min': 80000,
                'salary_max': 120000,
                'is_remote': True,
                'skills': 'UI/UX Design, Figma, Adobe Creative Suite, HTML, CSS, User Research'
            },
            {
                'title': 'DevOps Engineer',
                'description': 'Manage our cloud infrastructure and deployment pipelines. Help us scale our systems and improve our development workflow.',
                'location': 'Denver, CO',
                'salary_min': 110000,
                'salary_max': 160000,
                'is_remote': False,
                'skills': 'AWS, Docker, Kubernetes, Linux, Bash, CI/CD, Monitoring'
            },
            {
                'title': 'Full Stack Developer',
                'description': 'Work on both frontend and backend development. Build end-to-end features using modern web technologies.',
                'location': 'Boston, MA',
                'salary_min': 95000,
                'salary_max': 140000,
                'is_remote': True,
                'skills': 'JavaScript, Node.js, React, SQL, Git, REST APIs, AWS'
            },
            {
                'title': 'Digital Marketing Specialist',
                'description': 'Drive our digital marketing efforts including SEO, content marketing, and social media campaigns.',
                'location': 'Miami, FL',
                'salary_min': 60000,
                'salary_max': 90000,
                'is_remote': True,
                'skills': 'Digital Marketing, SEO, Content Writing, Social Media, Analytics, Google Ads'
            },
            {
                'title': 'Product Manager',
                'description': 'Lead product development initiatives and work with engineering teams to deliver customer-focused solutions.',
                'location': 'Chicago, IL',
                'salary_min': 100000,
                'salary_max': 150000,
                'is_remote': False,
                'skills': 'Product Management, Agile, Scrum, Leadership, Analytics, Communication'
            }
        ]

        created_count = 0
        for job_data in jobs_data:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                posted_by=recruiter_user,
                defaults={
                    'description': job_data['description'],
                    'location': job_data['location'],
                    'salary_min': job_data['salary_min'],
                    'salary_max': job_data['salary_max'],
                    'is_remote': job_data['is_remote'],
                    'skills': job_data['skills'],
                    'is_active': True,
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 30))
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created job: {job_data["title"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} dummy job postings!')
        )
