from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from inventory.models import BloodUnit, StockThreshold


@login_required
def home(request):
    units = BloodUnit.objects.all()

    total_units = units.count()
    available = units.filter(status=BloodUnit.Status.AVAILABLE).count()
    reserved = units.filter(status=BloodUnit.Status.RESERVED).count()
    issued = units.filter(status=BloodUnit.Status.ISSUED).count()

    # Units still available that expire within 3 days
    expiring_soon = [
        u for u in units.filter(status=BloodUnit.Status.AVAILABLE) if u.is_expiring_soon
    ]

    # Low stock: compare the AVAILABLE count for each blood group and
    # component against its threshold (default 5 if none is configured)
    thresholds = {
        (t.blood_group, t.component_type): t.minimum_units
        for t in StockThreshold.objects.all()
    }
    counts = (
        units.filter(status=BloodUnit.Status.AVAILABLE)
        .values('blood_group', 'component_type')
        .annotate(count=Count('id'))
    )
    counts_map = {(c['blood_group'], c['component_type']): c['count'] for c in counts}

    low_stock_groups = []
    for group, _ in BloodUnit.BloodGroup.choices:
        for component, _ in BloodUnit.Component.choices:
            minimum = thresholds.get((group, component), 5)
            available_count = counts_map.get((group, component), 0)
            if available_count < minimum:
                low_stock_groups.append({
                    'blood_group': group,
                    'component_type': component,
                    'available': available_count,
                    'minimum': minimum,
                })

    recent_units = units.order_by('-created_at')[:6]

    return render(request, 'dashboard/home.html', {
        'total_units': total_units,
        'available': available,
        'reserved': reserved,
        'issued': issued,
        'expiring_soon': expiring_soon,
        'low_stock_groups': low_stock_groups,
        'recent_units': recent_units,
    })