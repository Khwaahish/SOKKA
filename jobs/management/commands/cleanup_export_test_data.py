"""
Django management command to cleanup test data created for CSV export testing.
Run with: python manage.py cleanup_export_test_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from jobs.models import Job, JobApplication, EmailCommunication
from profiles.models import (
    Profile, ProfileSkill, Education, WorkExperience, 
    Link, UserProfile, ProfilePrivacySettings
)
from kanban.models import KanbanBoard, ProfileCard, ProfileLike


class Command(BaseCommand):
    help = 'Cleanup test data created by populate_export_test_data command'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        # Get confirmation unless --confirm flag is used
        if not options['confirm']:
            self.stdout.write(self.style.WARNING('\n⚠️  WARNING: This will delete all test data!'))
            self.stdout.write(self.style.WARNING('This includes:'))
            self.stdout.write('  • Test users (recruiters and job seekers)')
            self.stdout.write('  • Test jobs and applications')
            self.stdout.write('  • Email communications')
            self.stdout.write('  • Profile data (skills, experience, education)')
            self.stdout.write('  • Kanban boards and pipeline cards')
            self.stdout.write('  • Profile likes\n')
            
            confirmation = input('Are you sure you want to continue? (yes/no): ')
            if confirmation.lower() != 'yes':
                self.stdout.write(self.style.SUCCESS('Cleanup cancelled.'))
                return

        self.stdout.write(self.style.SUCCESS('\nStarting cleanup...'))
        
        # Track deletions
        counts = {}
        
        # Get test users (those with test_ prefix)
        test_users = User.objects.filter(username__startswith='test_')
        test_user_ids = list(test_users.values_list('id', flat=True))
        
        # Delete in order (respecting foreign key constraints)
        
        # 1. Profile Likes
        likes = ProfileLike.objects.filter(recruiter__in=test_user_ids)
        counts['profile_likes'] = likes.count()
        likes.delete()
        self.stdout.write(f'  ✓ Deleted {counts["profile_likes"]} profile likes')
        
        # 2. Profile Cards (Kanban)
        cards = ProfileCard.objects.filter(board__recruiter__in=test_user_ids)
        counts['profile_cards'] = cards.count()
        cards.delete()
        self.stdout.write(f'  ✓ Deleted {counts["profile_cards"]} profile cards')
        
        # 3. Kanban Boards
        boards = KanbanBoard.objects.filter(recruiter__in=test_user_ids)
        counts['kanban_boards'] = boards.count()
        boards.delete()
        self.stdout.write(f'  ✓ Deleted {counts["kanban_boards"]} kanban boards')
        
        # 4. Email Communications
        emails = EmailCommunication.objects.filter(sender__in=test_user_ids)
        counts['emails'] = emails.count()
        emails.delete()
        self.stdout.write(f'  ✓ Deleted {counts["emails"]} email communications')
        
        # 5. Job Applications
        applications = JobApplication.objects.filter(applicant__in=test_user_ids)
        counts['applications'] = applications.count()
        applications.delete()
        self.stdout.write(f'  ✓ Deleted {counts["applications"]} job applications')
        
        # 6. Jobs
        jobs = Job.objects.filter(posted_by__in=test_user_ids)
        counts['jobs'] = jobs.count()
        jobs.delete()
        self.stdout.write(f'  ✓ Deleted {counts["jobs"]} jobs')
        
        # 7. Links
        links = Link.objects.filter(profile__user__in=test_user_ids)
        counts['links'] = links.count()
        links.delete()
        self.stdout.write(f'  ✓ Deleted {counts["links"]} links')
        
        # 8. Work Experience
        experiences = WorkExperience.objects.filter(profile__user__in=test_user_ids)
        counts['work_experiences'] = experiences.count()
        experiences.delete()
        self.stdout.write(f'  ✓ Deleted {counts["work_experiences"]} work experiences')
        
        # 9. Education
        educations = Education.objects.filter(profile__user__in=test_user_ids)
        counts['educations'] = educations.count()
        educations.delete()
        self.stdout.write(f'  ✓ Deleted {counts["educations"]} education records')
        
        # 10. Profile Skills
        profile_skills = ProfileSkill.objects.filter(profile__user__in=test_user_ids)
        counts['profile_skills'] = profile_skills.count()
        profile_skills.delete()
        self.stdout.write(f'  ✓ Deleted {counts["profile_skills"]} profile skills')
        
        # 11. Profile Privacy Settings
        privacy_settings = ProfilePrivacySettings.objects.filter(profile__user__in=test_user_ids)
        counts['privacy_settings'] = privacy_settings.count()
        privacy_settings.delete()
        self.stdout.write(f'  ✓ Deleted {counts["privacy_settings"]} privacy settings')
        
        # 12. Profiles
        profiles = Profile.objects.filter(user__in=test_user_ids)
        counts['profiles'] = profiles.count()
        profiles.delete()
        self.stdout.write(f'  ✓ Deleted {counts["profiles"]} profiles')
        
        # 13. User Profiles
        user_profiles = UserProfile.objects.filter(user__in=test_user_ids)
        counts['user_profiles'] = user_profiles.count()
        user_profiles.delete()
        self.stdout.write(f'  ✓ Deleted {counts["user_profiles"]} user profiles')
        
        # 14. Finally, delete test users
        counts['users'] = test_users.count()
        test_users.delete()
        self.stdout.write(f'  ✓ Deleted {counts["users"]} test users')
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ CLEANUP COMPLETED SUCCESSFULLY!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'\n📊 Total items deleted:'))
        total = sum(counts.values())
        for key, value in counts.items():
            self.stdout.write(self.style.SUCCESS(f'  • {key.replace("_", " ").title()}: {value}'))
        self.stdout.write(self.style.SUCCESS(f'\n  TOTAL: {total} items deleted'))
        self.stdout.write(self.style.SUCCESS('\n🎉 Your database is now clean!\n'))

