from django.apps import apps
from django.utils import timezone
from django.db import IntegrityError

Sale = apps.get_model('sales_data', 'Sale')

print('initial_count', Sale.objects.count())
now = timezone.now()

# Create
s = Sale(product_name='UniqueTest', quantity=1, price=1.23, sale_date=now, customer_name='Tester', customer_email='unique_test@example.com')
s.save()
print('after_add', Sale.objects.count())

# Duplicate attempt
try:
    s2 = Sale(product_name='UniqueTest', quantity=2, price=2.34, sale_date=now, customer_name='Tester2', customer_email='unique_test@example.com')
    s2.save()
    print('duplicate_saved')
except IntegrityError as e:
    print('integrity_error', str(e))
except Exception as e:
    print('other_error', str(e))

# Update
s.product_name = 'UniqueTestUpdated'
s.save()
print('after_update', Sale.objects.filter(id=s.id).values_list('product_name', flat=True)[0])

# Search (case-insensitive)
results = list(Sale.objects.filter(product_name__icontains='uniquetest'))
print('search_found_count', len(results))

# Cleanup
Sale.objects.filter(customer_email='unique_test@example.com').delete()
print('after_cleanup', Sale.objects.count())
