from django.contrib import admin

from .models import Habit, HabitLog, Badge, UserBadge, Profile

admin.site.register(Habit)
admin.site.register(HabitLog)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(Profile)
