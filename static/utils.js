/**
 * Extra utility js functions.
 * Might consider using require.js
 */

// $fc is jquery selector for fullcalendar. e.g., $('#calendar')
function fullcalendar_refresh($fc) {
  $fc.fullCalendar('unselect');
  $fc.fullCalendar('refetchEvents');
  $fc.fullCalendar('rerenderEvents');
}

function display_ajax_messages() {
  $.get('/ajax_messages', function(data) {
    if (data.ajax_messages) {
      $('#main-page').prepend(data.ajax_messages);
    }
  });
}

function display_message(message, level) {
  var snippet = '<div class="alert fade in alert-' + level + ' alert-dismissible"><button type="button" class="close" data-dismiss="alert">&times;</button>' + message + '</div>';
  $('#main-page').prepend(snippet);
}