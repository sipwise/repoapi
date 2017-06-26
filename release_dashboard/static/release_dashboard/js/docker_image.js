$('button.delete').click(function(e){
  // don't send the form
  e.preventDefault();
  var button = $(this);
  var pk = button.attr('pk');
  var span = $('span#' + pk);
  var div = $('div.list-group-item#row_'+ pk);

  function successFunc(data, status) {
    span.html('Done');
    div.addClass("hidden");
  }

  function errorFunc(jqXHR, status, error) {
    span.html(error);
    button.removeAttr("disabled");
  }

  $.ajax({
    url: '/docker/tag/' + pk + '/',
    type: 'DELETE',
    success: successFunc,
    error: errorFunc,
    beforeSend: csrftokenFunc
  });

  //deactivate button
  button.attr("disabled", "disabled");
  span.html('processing');
  span.show();

});
