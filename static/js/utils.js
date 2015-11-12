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

function getRequestDay() {
  var day = getParameterByName('day');
  if (day) {
    return day;
  } else {
    return moment().format('YYYYMMDD');
  }
}

function getQueryString() {
  var pos = location.search.indexOf('?')
  if (pos != -1) {
    return location.search.substring(pos + 1);
  } else {
    return '';
  }
}

function checkEmail(email) {
  var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
  return re.test(email);
}

// make sure to be consistent with django DATETIME_INPUT_FORMATS settings.
function parseDatetime(dt_str) {
  var input_format = [
    'YYYY-MM-DD HH:mm',
    'MM/DD/YYYY HH:mm',
    'YYYY-MM-DD hh:mmA',
    'MM/DD/YYYY hh:mmA'
  ];
  var m = moment(dt_str, input_format);
  if (m.isValid()){
    return m;
  } else {
    return false;
  }
}

function is_viewport_xs() {
  // this selector is in base.html
  return $('#viewport-xs-detector').is(':hidden');
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

  var defaultEventRender = function(event, element, view) {
    // change fc-event link to go to the correct date/view.
    // note: change event.url has no effect. has to change the rendered element.

    var href = element.attr('href');
    // only add current url's query string if the event url does not have any query string.
    if (href && href.indexOf('?') == -1) {
      var queryString = getQueryString;
      if (queryString() != '') {
        element.attr('href', href + '?' + getQueryString());
      }
    }
  };

  var defaultDayClick = function(date, jsEvent, view) {
    // console.log(date);
    //console.log(jsEvent);
    var currentUrl = location.search;
    var newQueryString = '?' + 'day=' + date.format('YYYYMMDD') + '&view=agendaDay';
    var qsPos = currentUrl.indexOf('?')
    if (qsPos != -1) {
      window.location = currentUrl.substring(0, qsPos) + newQueryString;
    } else {
      window.location = currentUrl + newQueryString;
    }
  };

  return {
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'agendaDay,agendaWeek,month'
    },
    defaultDate: day.format('YYYY-MM-DD'),
    defaultView: param_view,

    fixedWeekCount: false,
    //allDaySlot: false,
    allDaySlot: true,
    allDayText: '',

    minTime: '06:00',
    maxTime: '21:00',
    scrollTime: '08:00',
    weekends: false,

    firstDay: 1,
    editable: false,
    eventLimit: true,

    eventRender: defaultEventRender,
    defaultEventRender: defaultEventRender,

    dayClick: defaultDayClick,
    defaultDayClick: defaultDayClick,

    //dayRender: function(date, cell) {
    //  //console.log(date);
    //  console.log(cell);
    //}
  };
}

function calendarChangeBookmark(view) {
  var current_day = view.calendar.getDate();
  var current_day_token = current_day.format('YYYYMMDD');
  var param_day = getParameterByName('day') || moment().format('YYYYMMDD');
  var param_view = getParameterByName('view') || 'agendaWeek';

  if (param_day != current_day.format('YYYYMMDD') || param_view != view.type) {
    window.history.pushState(current_day, null, './?day=' + current_day_token + '&view=' + view.calendar.getView().type);
  }
}

function defaultBootstrapSwitchOptions() {
  return {
    size: 'mini',
    onColor: 'success',
    // offColor: 'danger',
    onText: '<i class="fa fa-check"></i>',
    offText: '<i class="fa fa-minus"></i>',
  }
}

function resizeCards() {
  if (!is_viewport_xs()) {
    var maxHeight = 0;
    $('.card').each(function() {
      maxHeight = Math.max(maxHeight, $(this).height());
    });
    $('.card').height(maxHeight);
  }
}

// from isotope documentation about not doing filters every milisecond.
function debounce( fn, threshold ) {
  var timeout;
  return function debounced() {
    if (timeout) {
      clearTimeout(timeout);
    }
    function delayed() {
      fn();
      timeout = null;
    }
    timeout = setTimeout(delayed, threshold || 100);
  }
}