from django.contrib import admin
from django.contrib.auth.models import User
from .models import Company, Attendee , Venue,  Notification , Events , TicketType ,   BookNoww

# Register your models here.
admin.site.register(Attendee)
admin.site.register(Events)
admin.site.register(TicketType)
admin.site.register(Venue)


class BookNowwAdmin(admin.ModelAdmin):
    # Make sure that these fields exist in your BookNow model
    list_display = ['user', 'event', 'ticket_type', 'number_of_seats', 'booking_date']  # example fields


# Link the BookNow model with the BookNowAdmin class
admin.site.register(BookNoww, BookNowwAdmin)





class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.filter(user=request.user)
        return qs.none()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Notification, NotificationAdmin)



def activate_company(modeladmin, request, queryset):
    for company in queryset:
        company.is_active = True
        company.save()
        user = company.user
        user.is_active = True
        user.save()

        # Create a notification for the company manager
        Notification.objects.create(
            user=company.user,
            message=f'Your company account has been activated and you can now log in.'
        )

        # Optionally, you can also send an email notification here

activate_company.short_description = "Activate selected companies"

class CompanyAdmin(admin.ModelAdmin):
    actions = [activate_company]

admin.site.register(Company, CompanyAdmin)