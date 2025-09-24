// static/habits/js/main.js

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// AJAX setup for Django csrf
$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    }
  }
});

// Mark complete click handler
$(document).on('click', '.mark-complete', function(e) {
  e.preventDefault();
  const btn = $(this); const habitId = btn.data('habit-id');
  btn.prop('disabled', true).text('Marking...');
  $.post('/ajax/mark-complete/', { 'habit_id': habitId })
    .done(function(data) {
      if (data.status === 'ok') {
        $('#points').text(data.points);
        $('#level').text(data.level);
        // show awarded badges (simple alert for now)
        if (data.awarded && data.awarded.length) {
          alert('New badges: ' + data.awarded.join(', '));
        }
        btn.text('Done').addClass('btn-success');
      } else if (data.status === 'exists') {
        alert(data.message);
        btn.text('Done').addClass('btn-success');
      } else {
        alert('Error: ' + data.message);
        btn.prop('disabled', false).text('Mark Done');
      }
    })
    .fail(function(xhr){
      alert('Request failed');
      btn.prop('disabled', false).text('Mark Done');
    });
});

// Chart.js render (weekly)
if (typeof chartDays !== 'undefined') {
  const ctx = document.getElementById('weeklyChart');
  if (ctx) {
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: chartDays,
        datasets: [{
          label: 'Habits completed',
          data: chartCounts,
          fill: false,
          tension: 0.4,
        }]
      },
      options: { responsive: true }
    });
  }
}