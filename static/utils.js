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