/**
 * refresh info
 */
$('button#refresh_all').click(function(e){
  // don't send the form
  e.preventDefault();
  var button = $(this);
  var span = $('span#refresh_all_error');

  $.ajax({
    url: '/release_panel/refresh/',
    type: 'POST',
    success: successFunc,
    error: errorFunc,
    beforeSend: csrftokenFunc
  });

  function successFunc(data, status) {
    span.html('');
    span.append('<a href="' + data.url + '">Done</a><br/>');
    span.append('This will take a while. Refresh the page in a few');
  }

  function errorFunc(jqXHR, status, error) {
    span.html(error);
    button.removeAttr("disabled");
  }

  //deactivate button
  button.attr("disabled", "disabled");
  span.html('processing');
  span.show();
});

$('button.refresh').click(function(e){
  // don't send the form
  e.preventDefault();
  var button = $(this);
  var project = button.attr('id').replace('refresh_','');
  var span = $('span#refresh_error_' + project );

  function successFunc(data, status) {
    span.html('');
    span.append('<a href="' + data.url + '">Done</a>');
    button.removeAttr("disabled");
  }

  function errorFunc(jqXHR, status, error) {
    span.html(error);
    button.removeAttr("disabled");
  }

  $.ajax({
    url: '/release_panel/refresh/' + project + '/',
    type: 'POST',
    success: successFunc,
    error: errorFunc,
    beforeSend: csrftokenFunc
  });

  //deactivate button
  button.attr("disabled", "disabled");
  span.html('processing');
  span.show();

});
