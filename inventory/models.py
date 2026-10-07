import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class BloodUnit(models.Model):
    """One physical unit of donated blood, or a component separated from it."""

    class BloodGroup(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'

    class Component(models.TextChoices):
        WHOLE_BLOOD = 'WHOLE_RBC', 'Whole Blood / RBC'
        PLASMA = 'PLASMA', 'Plasma'
        PLATELETS = 'PLATELETS', 'Platelets'

    # Shelf life per component, in days
    SHELF_LIFE_DAYS = {
        Component.WHOLE_BLOOD: 35,
        Component.PLASMA: 365,
        Component.PLATELETS: 5,
    }

    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        RESERVED = 'RESERVED', 'Reserved'
        ISSUED = 'ISSUED', 'Issued'
        EXPIRED = 'EXPIRED', 'Expired'

    unit_id = models.CharField(max_length=12, unique=True, editable=False)
    blood_group = models.CharField(max_length=3, choices=BloodGroup.choices)
    component_type = models.CharField(max_length=10, choices=Component.choices)
    collection_date = models.DateField()
    expiry_date = models.DateField(editable=False)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='units_added'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['expiry_date']

    def save(self, *args, **kwargs):
        if not self.unit_id:
            self.unit_id = f"BU-{uuid.uuid4().hex[:8].upper()}"
        if self.collection_date and not self.expiry_date:
            shelf_life = self.SHELF_LIFE_DAYS[self.component_type]
            self.expiry_date = self.collection_date + timedelta(days=shelf_life)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unit_id} · {self.blood_group} · {self.get_component_type_display()}"

    @property
    def is_expired(self):
        return self.expiry_date < timezone.localdate()

    @property
    def days_to_expiry(self):
        return (self.expiry_date - timezone.localdate()).days

    @property
    def is_expiring_soon(self):
        return self.status == self.Status.AVAILABLE and 0 <= self.days_to_expiry <= 3

    def can_be_reserved(self):
        return self.status == self.Status.AVAILABLE and not self.is_expired

    def can_be_issued(self):
        return self.status == self.Status.RESERVED


class Reservation(models.Model):
    """Cross-match record. Creating one locks the unit as RESERVED."""

    unit = models.OneToOneField(BloodUnit, on_delete=models.CASCADE, related_name='reservation')
    patient_name = models.CharField(max_length=120)
    ward_or_department = models.CharField(max_length=120, blank=True)
    reserved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reserved_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Reservation for {self.unit.unit_id} - {self.patient_name}"


class IssueRecord(models.Model):
    """Final handoff of a reserved unit to a patient."""

    unit = models.OneToOneField(BloodUnit, on_delete=models.CASCADE, related_name='issue_record')
    issued_to = models.CharField(max_length=120)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Issued {self.unit.unit_id} to {self.issued_to}"


class StockThreshold(models.Model):
    """Minimum available units per blood group and component before it counts as low stock."""

    blood_group = models.CharField(max_length=3, choices=BloodUnit.BloodGroup.choices)
    component_type = models.CharField(max_length=10, choices=BloodUnit.Component.choices)
    minimum_units = models.PositiveIntegerField(default=5)

    class Meta:
        unique_together = ('blood_group', 'component_type')

    def __str__(self):
        return f"{self.blood_group} / {self.get_component_type_display()} min {self.minimum_units}"