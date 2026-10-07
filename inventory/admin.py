from django.contrib import admin
from .models import BloodUnit, Reservation, IssueRecord, StockThreshold


@admin.register(BloodUnit)
class BloodUnitAdmin(admin.ModelAdmin):
    list_display = ('unit_id', 'blood_group', 'component_type', 'status', 'collection_date', 'expiry_date')
    list_filter = ('blood_group', 'component_type', 'status')
    search_fields = ('unit_id',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('unit', 'patient_name', 'reserved_by', 'reserved_at')


@admin.register(IssueRecord)
class IssueRecordAdmin(admin.ModelAdmin):
    list_display = ('unit', 'issued_to', 'issued_by', 'issued_at')


@admin.register(StockThreshold)
class StockThresholdAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'component_type', 'minimum_units')