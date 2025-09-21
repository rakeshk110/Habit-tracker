from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from datetime import date, timedelta
from .models import Habit, HabitLog, Profile, Badge, UserBadge
from .forms import HabitForm, SignUpForm


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form':form})

@login_required
def dashboard(request):
    habits = Habit.objects.filter(user=request.user)
    profile = request.user.profile
    badges = UserBadge.objects.filter(user=request.user).select_related('badge')

    today = date.today()
    days = []
    counts = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        days.append(d.strftime('%a'))
    counts.append(HabitLog.objects.filter(habit=request.user, date=d, completed=True).count())
    context = {
        'habits': habits,
        'profile': profile,
        'badges': badges,
        'chart_days': days,
        'chart_counts': counts,
    }
    return render(request, 'habits/dashboard.html', context)

@login_required
def habit_create(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            return redirect('dashboard')
        else:
            form = HabitForm()
        return render(request, 'habits/habit_form.html', {'form': form})
@login_required
def habit_update(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = HabitForm(instance=habit)
    return render(request, 'habits/habit_form.html', {'form':form})

@login_required
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    if request.method == 'POST':
        habit.delete()
        return redirect('dashboard')
    return render(request, 'habits/habit_confirm_delete.html', {'habit': habit})

from django.views.decorators.http import require_POST

@login_required
@require_POST
def mark_complete(request):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message':'Invalid request type.'})
    habit_id = request.POST.get('habit_id')
    habit = get_object_or_404(Habit, pk=habit_id, user=request.user)
    today = date.today()

    log, created = HabitLog.objects.get_or_create(habit=habit, date=today, defaults={'completed': True})
    if not created:
        return JsonResponse({'status': 'exists', 'message': 'Already marked for today.'})
    profile = request.user.profile
    POINTS_PER_HABIT = 10
    profile.points += POINTS_PER_HABIT
    profile.update_level()
    profile.save()

    streak = habit.current_streack()

    awarded = []
    streak_badges = Badge.objects.filter(streak_required__isnull=False, streak_required__lte=streak)
    for b in streak_badges:
        ub, ub_created = UserBadge.objects.get_or_create(user=request.user, badge=b)
        if ub_created:
            awarded.append(b.name)
        points_badge = Badge.objects.filter(points_required__isnull=False, points_required_lte=profile.points)
        for b in points_badge:
            ub, ub_created = UserBadge.objects.get_or_create(user=request.user, badge=b)
            if ub_created:
                awarded.append(b.name)
            data = {
                'status' : 'ok',
                'points' : profile.points,
                'level' : profile.level,
                'status' : streak,
                'status' : awarded,
            }
        return JsonResponse(data)
    
@login_required
def leaderboard(request):
    top_profiles = Profile.objects.selcet_related('user').order_by('-points')[:10]
    return render(request, 'habits/leaderboard.html', {'profiles': top_profiles})
