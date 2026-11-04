from django.contrib import admin
from .models import (Department,Category,Complaint,Attachment,Comment,ActivityLog,)

# Register your models here.
admin.site.register(Department)
admin.site.register(Category)
admin.site.register(Attachment)
admin.site.register(Comment)
admin.site.register(ActivityLog)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = (
        "tracking_id",
        "title",
        "citizen",
        "category",
        "status",
        "priority",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "category",
        "created_at",
    )

    search_fields = (
        "tracking_id",
        "title",
        "citizen__username",
        "category__name",
    )

    ordering = ("-created_at",)

    list_per_page = 20