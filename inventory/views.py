from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.decorators import admin_required
from .forms import BloodUnitForm, ReservationForm, IssueForm, InventoryFilterForm
from .models import BloodUnit


@login_required
def unit_list(request):
    units = BloodUnit.objects.select_related('created_by').all()
    form = InventoryFilterForm(request.GET or None)

    if form.is_valid():
        if form.cleaned_data['blood_group']:
            units = units.filter(blood_group=form.cleaned_data['blood_group'])
        if form.cleaned_data['component_type']:
            units = units.filter(component_type=form.cleaned_data['component_type'])
        if form.cleaned_data['status']:
            units = units.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['q']:
            units = units.filter(unit_id__icontains=form.cleaned_data['q'])

    paginator = Paginator(units, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'inventory/unit_list.html', {
        'page_obj': page_obj,
        'filter_form': form,
    })


@login_required
def unit_detail(request, pk):
    unit = get_object_or_404(BloodUnit, pk=pk)
    return render(request, 'inventory/unit_detail.html', {'unit': unit})


@login_required
def unit_add(request):
    form = BloodUnitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        unit = form.save(commit=False)
        unit.created_by = request.user
        unit.save()
        messages.success(request, f"{unit.unit_id} added to inventory.")
        return redirect('inventory:unit_detail', pk=unit.pk)
    return render(request, 'inventory/unit_form.html', {'form': form})


@admin_required
def unit_delete(request, pk):
    unit = get_object_or_404(BloodUnit, pk=pk)
    if request.method == 'POST':
        unit.delete()
        messages.success(request, f"{unit.unit_id} removed.")
        return redirect('inventory:unit_list')
    return render(request, 'inventory/unit_confirm_delete.html', {'unit': unit})


@login_required
def unit_reserve(request, pk):
    unit = get_object_or_404(BloodUnit, pk=pk)
    if not unit.can_be_reserved():
        messages.error(request, "This unit can't be reserved right now.")
        return redirect('inventory:unit_detail', pk=pk)

    form = ReservationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        reservation = form.save(commit=False)
        reservation.unit = unit
        reservation.reserved_by = request.user
        reservation.save()
        unit.status = BloodUnit.Status.RESERVED
        unit.save(update_fields=['status'])
        messages.success(request, f"{unit.unit_id} reserved for {reservation.patient_name}.")
        return redirect('inventory:unit_detail', pk=pk)
    return render(request, 'inventory/unit_reserve.html', {'form': form, 'unit': unit})


@login_required
def unit_release(request, pk):
    unit = get_object_or_404(BloodUnit, pk=pk)
    if request.method == 'POST' and unit.status == BloodUnit.Status.RESERVED:
        reservation = getattr(unit, 'reservation', None)
        if reservation:
            reservation.delete()
        unit.status = BloodUnit.Status.AVAILABLE
        unit.save(update_fields=['status'])
        messages.success(request, f"{unit.unit_id} released back to available stock.")
    return redirect('inventory:unit_detail', pk=pk)


@login_required
def unit_issue(request, pk):
    unit = get_object_or_404(BloodUnit, pk=pk)
    if not unit.can_be_issued():
        messages.error(request, "Only reserved units can be issued.")
        return redirect('inventory:unit_detail', pk=pk)

    form = IssueForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        issue = form.save(commit=False)
        issue.unit = unit
        issue.issued_by = request.user
        issue.save()
        unit.status = BloodUnit.Status.ISSUED
        unit.save(update_fields=['status'])
        messages.success(request, f"{unit.unit_id} issued to {issue.issued_to}.")
        return redirect('inventory:unit_detail', pk=pk)
    return render(request, 'inventory/unit_issue.html', {'form': form, 'unit': unit})