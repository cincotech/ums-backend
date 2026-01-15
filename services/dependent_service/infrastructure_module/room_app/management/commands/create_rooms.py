from django.core.management.base import BaseCommand
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.dependent_service.infrastructure_module.building_app.models import Building


class Command(BaseCommand):
    help = 'Create rooms with ranges 100-150, 200-250, 300-350'

    def add_arguments(self, parser):
        parser.add_argument('--building-id', type=str, help='Building UUID')
        parser.add_argument('--building-name', type=str, help='Building name')

    def handle(self, *args, **options):
        building_id = options.get('building_id')
        building_name = options.get('building_name')

        if building_id:
            building = Building.objects.get(id=building_id)
        elif building_name:
            building = Building.objects.get(building_name=building_name)
        else:
            building = Building.objects.first()
            if not building:
                self.stdout.write(self.style.ERROR('No building found. Create a building first.'))
                return

        ranges = [(100, 150), (200, 250), (300, 350)]
        created_count = 0

        for start, end in ranges:
            for num in range(start, end + 1):
                room_name = f"Room {num}"
                room_code = str(num)
                
                if not Room.objects.filter(room_code=room_code, building=building).exists():
                    Room.objects.create(
                        building=building,
                        room_name=room_name,
                        room_code=room_code,
                        capacity=30,
                        room_type='classroom',
                        is_available=True
                    )
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} rooms in {building.building_name}')
        )
