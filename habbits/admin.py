from django.contrib import admin

from habbits.models import Habit, HabitCompletion


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("id", "place", "time", "action", "duration", "owner")
    list_filter = ("owner",)
    search_fields = ("place", "action")


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ("habit", "completed_at", "note")
    search_fields = ("completed_at",)
