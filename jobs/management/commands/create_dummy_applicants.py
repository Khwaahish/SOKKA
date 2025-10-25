from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profiles.models import UserProfile, Profile, Skill, ProfileSkill, Education, WorkExperience
from django.utils import timezone
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create dummy job seekers with profiles and skills'

    def handle(self, *args, **options):
        # Skills to use
        skills_data = [
            'Python', 'JavaScript', 'React', 'Django', 'Node.js', 'SQL', 'HTML', 'CSS',
            'Machine Learning', 'Data Analysis', 'Project Management', 'Agile', 'Scrum',
            'AWS', 'Docker', 'Git', 'REST APIs', 'GraphQL', 'MongoDB', 'PostgreSQL',
            'Java', 'Spring Boot', 'Angular', 'Vue.js', 'TypeScript', 'C++', 'C#',
            'DevOps', 'Kubernetes', 'Linux', 'Bash', 'PHP', 'Laravel', 'Ruby', 'Rails',
            'UI/UX Design', 'Figma', 'Adobe Creative Suite', 'Photoshop', 'Illustrator',
            'Marketing', 'Digital Marketing', 'SEO', 'Content Writing', 'Social Media',
            'Sales', 'Customer Service', 'Business Development', 'Finance', 'Accounting',
            'HR', 'Recruitment', 'Training', 'Leadership', 'Communication'
        ]

        # Create skills if they don't exist
        for skill_name in skills_data:
            Skill.objects.get_or_create(name=skill_name)

        # Dummy job seekers data
        job_seekers_data = [
            {
                'username': 'john_developer',
                'email': 'john.developer@email.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'headline': 'Full Stack Developer',
                'bio': 'Passionate full-stack developer with 5 years of experience building web applications.',
                'location': 'San Francisco, CA',
                'skills': ['Python', 'Django', 'React', 'JavaScript', 'SQL', 'AWS', 'Git']
            },
            {
                'username': 'sarah_designer',
                'email': 'sarah.designer@email.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'headline': 'UI/UX Designer',
                'bio': 'Creative UI/UX designer with expertise in user-centered design and modern web interfaces.',
                'location': 'New York, NY',
                'skills': ['UI/UX Design', 'Figma', 'Adobe Creative Suite', 'HTML', 'CSS', 'JavaScript', 'Photoshop']
            },
            {
                'username': 'mike_data',
                'email': 'mike.analyst@email.com',
                'first_name': 'Mike',
                'last_name': 'Chen',
                'headline': 'Data Scientist',
                'bio': 'Data scientist specializing in machine learning and statistical analysis.',
                'location': 'Seattle, WA',
                'skills': ['Python', 'Machine Learning', 'Data Analysis', 'SQL', 'R', 'AWS', 'Docker']
            },
            {
                'username': 'lisa_marketing',
                'email': 'lisa.marketing@email.com',
                'first_name': 'Lisa',
                'last_name': 'Williams',
                'headline': 'Digital Marketing Specialist',
                'bio': 'Digital marketing expert with proven track record in SEO, content marketing, and social media.',
                'location': 'Austin, TX',
                'skills': ['Digital Marketing', 'SEO', 'Content Writing', 'Social Media', 'Analytics', 'Google Ads']
            },
            {
                'username': 'david_engineer',
                'email': 'david.engineer@email.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'headline': 'Software Engineer',
                'bio': 'Experienced software engineer with expertise in Java, Spring Boot, and microservices architecture.',
                'location': 'Boston, MA',
                'skills': ['Java', 'Spring Boot', 'Microservices', 'SQL', 'Docker', 'Kubernetes', 'AWS']
            },
            {
                'username': 'emma_frontend',
                'email': 'emma.frontend@email.com',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'headline': 'Frontend Developer',
                'bio': 'Frontend developer passionate about creating beautiful, responsive user interfaces.',
                'location': 'Portland, OR',
                'skills': ['React', 'Vue.js', 'TypeScript', 'HTML', 'CSS', 'JavaScript', 'Node.js']
            },
            {
                'username': 'alex_devops',
                'email': 'alex.devops@email.com',
                'first_name': 'Alex',
                'last_name': 'Wilson',
                'headline': 'DevOps Engineer',
                'bio': 'DevOps engineer with expertise in cloud infrastructure, CI/CD, and automation.',
                'location': 'Denver, CO',
                'skills': ['DevOps', 'AWS', 'Docker', 'Kubernetes', 'Linux', 'Bash', 'Git']
            },
            {
                'username': 'jessica_product',
                'email': 'jessica.product@email.com',
                'first_name': 'Jessica',
                'last_name': 'Taylor',
                'headline': 'Product Manager',
                'bio': 'Product manager with experience in agile development and cross-functional team leadership.',
                'location': 'Chicago, IL',
                'skills': ['Product Management', 'Agile', 'Scrum', 'Leadership', 'Communication', 'Analytics']
            },
            {
                'username': 'ryan_mobile',
                'email': 'ryan.mobile@email.com',
                'first_name': 'Ryan',
                'last_name': 'Anderson',
                'headline': 'Mobile App Developer',
                'bio': 'Mobile app developer specializing in iOS and Android development.',
                'location': 'Miami, FL',
                'skills': ['iOS Development', 'Android Development', 'Swift', 'Kotlin', 'React Native', 'JavaScript']
            },
            {
                'username': 'maria_backend',
                'email': 'maria.backend@email.com',
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'headline': 'Backend Developer',
                'bio': 'Backend developer with expertise in API development and database design.',
                'location': 'Phoenix, AZ',
                'skills': ['Python', 'Django', 'REST APIs', 'PostgreSQL', 'MongoDB', 'Redis', 'AWS']
            }
        ]

        created_count = 0
        for seeker_data in job_seekers_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=seeker_data['username'],
                defaults={
                    'email': seeker_data['email'],
                    'first_name': seeker_data['first_name'],
                    'last_name': seeker_data['last_name']
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                # Create UserProfile as job seeker
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'user_type': 'job_seeker'}
                )
                
                # Create Profile
                profile, profile_created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'headline': seeker_data['headline'],
                        'bio': seeker_data['bio'],
                        'location': seeker_data['location']
                    }
                )
                
                if profile_created:
                    # Add skills to profile
                    for skill_name in seeker_data['skills']:
                        skill, _ = Skill.objects.get_or_create(name=skill_name)
                        ProfileSkill.objects.get_or_create(profile=profile, skill=skill)
                    
                    # Add some education
                    Education.objects.create(
                        profile=profile,
                        institution=f"{seeker_data['first_name']} University",
                        degree="Bachelor's Degree",
                        field_of_study="Computer Science",
                        start_date=timezone.now() - timedelta(days=1460),  # 4 years ago
                        end_date=timezone.now() - timedelta(days=365),  # 1 year ago
                        is_current=False
                    )
                    
                    # Add work experience
                    WorkExperience.objects.create(
                        profile=profile,
                        company=f"{seeker_data['first_name']} Tech Solutions",
                        position=seeker_data['headline'],
                        description=f"Worked as a {seeker_data['headline'].lower()} with focus on modern technologies and best practices.",
                        start_date=timezone.now() - timedelta(days=730),  # 2 years ago
                        end_date=None,
                        is_current=True
                    )
                    
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created job seeker: {seeker_data["first_name"]} {seeker_data["last_name"]}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} dummy job seekers!')
        )
