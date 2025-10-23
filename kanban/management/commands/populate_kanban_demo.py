from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from kanban.models import PipelineStage, KanbanBoard, ProfileCard
from profiles.models import Profile
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate the kanban board with demo data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n🚀 Starting Kanban Board Demo Setup...\n'))
        
        # Step 1: Initialize pipeline stages
        self.stdout.write(self.style.HTTP_INFO('Step 1: Creating pipeline stages...'))
        stages_data = [
            ('profile_interest', 'Profile Interest', '#667eea', 0),
            ('resume_review', 'Resume Review', '#43e97b', 1),
            ('interview', 'Interview', '#4facfe', 2),
            ('hired', 'Hired', '#38b2ac', 3),
            ('rejected', 'Rejected', '#fa709a', 4),
        ]
        
        stages = {}
        for name, display_name, color, order in stages_data:
            stage, created = PipelineStage.objects.get_or_create(
                name=name,
                defaults={'order': order, 'color': color}
            )
            stages[name] = stage
            status = '✓ Created' if created else '• Already exists'
            self.stdout.write(f'  {status}: {display_name}')
        
        # Step 2: Get or create a recruiter user
        self.stdout.write(self.style.HTTP_INFO('\nStep 2: Setting up recruiter user...'))
        recruiter_group, _ = Group.objects.get_or_create(name='Recruiter')
        
        # Try to get existing user or create a demo recruiter
        try:
            recruiter = User.objects.filter(groups__name='Recruiter').first()
            if not recruiter:
                recruiter = User.objects.create_user(
                    username='demo_recruiter',
                    email='recruiter@sokka.com',
                    password='demo1234',
                    first_name='Demo',
                    last_name='Recruiter'
                )
                recruiter.groups.add(recruiter_group)
                self.stdout.write(f'  ✓ Created demo recruiter: demo_recruiter (password: demo1234)')
            else:
                self.stdout.write(f'  • Using existing recruiter: {recruiter.username}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Error creating recruiter: {e}'))
            return
        
        # Step 3: Get or create kanban board
        self.stdout.write(self.style.HTTP_INFO('\nStep 3: Creating kanban board...'))
        board, created = KanbanBoard.objects.get_or_create(
            recruiter=recruiter,
            defaults={'name': 'Demo Hiring Pipeline'}
        )
        status = '✓ Created' if created else '• Already exists'
        self.stdout.write(f'  {status}: {board.name}')
        
        # Step 4: Create sample profiles
        self.stdout.write(self.style.HTTP_INFO('\nStep 4: Creating sample candidate profiles...'))
        
        profiles_data = [
            {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'headline': 'Senior Software Engineer',
                'location': 'San Francisco, CA',
                'bio': 'Full-stack developer with 8 years of experience',
                'stage': 'profile_interest'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Chen',
                'headline': 'Frontend Developer',
                'location': 'Seattle, WA',
                'bio': 'React specialist with passion for UI/UX',
                'stage': 'profile_interest'
            },
            {
                'first_name': 'Emily',
                'last_name': 'Rodriguez',
                'headline': 'DevOps Engineer',
                'location': 'Austin, TX',
                'bio': 'Cloud infrastructure and automation expert',
                'stage': 'resume_review'
            },
            {
                'first_name': 'James',
                'last_name': 'Wilson',
                'headline': 'Backend Developer',
                'location': 'New York, NY',
                'bio': 'Python and Django specialist',
                'stage': 'resume_review'
            },
            {
                'first_name': 'Aisha',
                'last_name': 'Patel',
                'headline': 'Data Scientist',
                'location': 'Boston, MA',
                'bio': 'ML engineer with PhD in Computer Science',
                'stage': 'interview'
            },
            {
                'first_name': 'David',
                'last_name': 'Kim',
                'headline': 'Mobile Developer',
                'location': 'Los Angeles, CA',
                'bio': 'iOS and Android development expert',
                'stage': 'interview'
            },
            {
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'headline': 'Product Manager',
                'location': 'Chicago, IL',
                'bio': 'Technical PM with engineering background',
                'stage': 'hired'
            },
            {
                'first_name': 'Robert',
                'last_name': 'Thompson',
                'headline': 'Security Engineer',
                'location': 'Denver, CO',
                'bio': 'Cybersecurity specialist and ethical hacker',
                'stage': 'rejected'
            },
        ]
        
        created_profiles = 0
        for profile_data in profiles_data:
            stage_name = profile_data.pop('stage')
            
            # Create user for profile
            username = f"{profile_data['first_name'].lower()}_{profile_data['last_name'].lower()}"
            email = f"{username}@example.com"
            
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': profile_data['first_name'],
                    'last_name': profile_data['last_name']
                }
            )
            
            # Create profile
            profile, profile_created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': profile_data['first_name'],
                    'last_name': profile_data['last_name'],
                    'headline': profile_data['headline'],
                    'location': profile_data['location'],
                    'bio': profile_data['bio'],
                }
            )
            
            # Add to kanban board
            card, card_created = ProfileCard.objects.get_or_create(
                board=board,
                profile=profile,
                defaults={
                    'stage': stages[stage_name],
                    'position': 0
                }
            )
            
            if card_created:
                created_profiles += 1
                self.stdout.write(
                    f'  ✓ Added {profile.get_full_name()} to {stages[stage_name].get_name_display()}'
                )
            else:
                self.stdout.write(
                    f'  • {profile.get_full_name()} already in pipeline'
                )
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✨ KANBAN BOARD DEMO SETUP COMPLETE! ✨'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        total_cards = ProfileCard.objects.filter(board=board).count()
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  • Pipeline Stages: {len(stages)}')
        self.stdout.write(f'  • Candidate Profiles: {total_cards}')
        self.stdout.write(f'  • Board Owner: {recruiter.get_full_name()} ({recruiter.username})')
        
        self.stdout.write(f'\n🌐 To view the kanban board:')
        self.stdout.write(f'  1. Start the server: python manage.py runserver')
        self.stdout.write(f'  2. Login as: {recruiter.username}')
        if recruiter.username == 'demo_recruiter':
            self.stdout.write(f'     Password: demo1234')
        self.stdout.write(f'  3. Visit: http://127.0.0.1:8000/kanban/')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Setup completed successfully!\n'))

