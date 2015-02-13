/**
 * Extra utility js functions.
 * Might consider using require.js
 */

function display_ajax_messages() {
  $.get('/ajax_messages', function(data) {
    if (data.ajax_messages) {
      // someday: re-enable once the messages system is fully designed.
      console.log(data.ajax_messages);
      //$('#main-page').prepend(data.ajax_messages);
    }
  });
}

function display_message(message, level) {
  var snippet = '<div class="alert fade in alert-' + level + ' alert-dismissible"><button type="button" class="close" data-dismiss="alert">&times;</button>' + message + '</div>';
  $('#main-page').prepend(snippet);
}

function getParameterByName(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
    results = regex.exec(location.search);
  return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

////////////////////    full calendar related    ////////////////////////

// $fc is jquery selector for fullcalendar. e.g., $('#calendar')
function fullcalendar_refresh($fc) {
  $fc.fullCalendar('unselect');
  $fc.fullCalendar('refetchEvents');
  $fc.fullCalendar('rerenderEvents');
}

function getCalendarDefaults() {
  var param_day = getParameterByName('day');
  var day = param_day ? moment(param_day, 'YYYYMMDD') : moment();
  var param_view = getParameterByName('view') || 'agendaWeek';

  return {
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'agendaDay,agendaWeek,month'
    },
    defaultDate: day.format('YYYY-MM-DD'),
    defaultView: param_view,

    fixedWeekCount: false,
    allDaySlot: false,

    minTime: '06:00',
    maxTime: '21:00',
    scrollTime: '08:00',

    firstDay: 1,
    editable: false,
    eventLimit: true
  };
}

function calendarChangeBookmark(view) {
  var current_day = view.calendar.getDate();
  var current_day_token = current_day.format('YYYYMMDD');
  var param_day = getParameterByName('day') || moment().format('YYYYMMDD');
  if (param_day != current_day.format('YYYYMMDD')) {
    window.history.pushState(current_day, null, './?day=' + current_day_token + '&view=' + view.calendar.getView().type);
  }
}