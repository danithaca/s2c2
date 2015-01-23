jQuery(document).ready(function() {
  // for edit page only. use phone formatter
  jQuery('.phone-number').each(function(i, e) {
    new Formatter(e, {
      'pattern': "{{999}}-{{999}}-{{9999}}",
      'persistent': false
    });
  });
  //new Formatter(document.getElementById('id_phone_main'), {
  //  'pattern': "{{999}}-{{999}}-{{9999}}",
  //  'persistent': true
  //});
  //jQuery('.phone-main').formatter({
  //    'pattern': "{{999}}-{{999}}-{{9999}}",
  //    'persistent': true
  //});
});