import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import StaffUser
from inventory.models import BloodUnit, StockThreshold


class Command(BaseCommand):
    help = "Seed the database with realistic demo blood units."

    def handle(self, *args, **options):
        admin = StaffUser.objects.filter(role='ADMIN').first()
        if not admin:
            self.stdout.write(self.style.ERROR('No admin user found. Create one first.'))
            return

        today = timezone.localdate()
        groups = [g[0] for g in BloodUnit.BloodGroup.choices]
        components = [c[0] for c in BloodUnit.Component.choices]

        # Keep most units realistically fresh, with a few pushed close to
        # expiry so the dashboard's alert panel has something to show.
        age_ranges = {
            BloodUnit.Component.WHOLE_BLOOD: (0, 34),
            BloodUnit.Component.PLASMA: (0, 200),
            BloodUnit.Component.PLATELETS: (0, 4),
        }

        created = 0
        for _ in range(40):
            group = random.choice(groups)
            component = random.choice(components)
            low, high = age_ranges[component]
            days_ago = random.randint(low, high)
            unit = BloodUnit(
                blood_group=group,
                component_type=component,
                collection_date=today - timedelta(days=days_ago),
                created_by=admin,
            )
            unit.save()
            created += 1

        for group in groups:
            for component in components:
                StockThreshold.objects.get_or_create(
                    blood_group=group, component_type=component, defaults={'minimum_units': 2}
                )

        self.stdout.write(self.style.SUCCESS(f'Created {created} blood units.'))