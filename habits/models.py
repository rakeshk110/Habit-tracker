from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def update_level(self):

        self.level = (self.points // 100) + 1
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.points} pts"
    
class Badge(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    streak_required = models.IntegerField(null=True, blank=True)
    points_required = models.IntegerField(null=True, blank=True)
    icon = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name
    
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
    
class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),

    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    title = models.CharField(max_length=200)
    description =models.TextField(blank=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def current_streak(self):
        today = date.today()
        streak = 0 
        check_day = today
        while True:
            exists = HabitLog.objects.filter(habit=self, date=check_day, completed=True).exists()
            if exists:
                streak += 1
                check_day = check_day - timedelta(days=1)
            else:
                break
        return streak
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    

class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    completed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('habit', 'date')
        
    def __str__(self):
        return f"{self.habit.title} - {self.date} - {'Done' if self.completed else 'Missed'}"
    
