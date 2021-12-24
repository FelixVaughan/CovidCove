from django.db.models import Count, Max
from .models import Global, Country

unique_fields = ['name', 'time_as_string']

duplicates = (
    Global.objects.values(*unique_fields)
    .order_by()
    .annotate(max_id=Max('id'), count_id=Count('id'))
    .filter(count_id__gt=1)
)

for duplicate in duplicates:
    (
        Global.objects
        .filter(**{x: duplicate[x] for x in unique_fields})
        .exclude(id=duplicate['max_id'])
        .delete()
    )