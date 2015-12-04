/**
 *
 *
 */
function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function csrftokenFunc(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
var csrftoken = getCookie('csrftoken');

$('button.hotfix').click(function(e){
  // don't send the form
  e.preventDefault();
  var button = $(this);
  var id = button.attr('id').replace('hotfix_','');
  var branch = $('select#version_' + id + ' option:selected').val().replace('branch/', '');
  var repo = id;
  var span = $('span#hotfix_error_' + id);

  $.ajax({
    url: 'hotfix/' + branch + '/' + repo + '/',
    type: 'POST',
    success: successFunc,
    error: errorFunc,
    beforeSend: csrftokenFunc
  });

  //deactivate button
  button.attr("disabled", "disabled");
  span.html('processing');
  span.show();

  function successFunc(data, status) {
    span.html('');
    span.append('<a href="' + data.url + '">Done</a>');
    button.removeAttr("disabled");
  }

  function errorFunc(jqXHR, status, error) {
    span.html(error);
    button.removeAttr("disabled");
  }
});

$('td.version > select').change(function() {
  var id = $(this).attr('id').replace('version_','');
  var version = $(this).val();
  if (version.match(/^branch\/mr[0-9]+\.[0-9]+\.[0-9]+$/)) {
    $('button#hotfix_' + id).show();
  }
  else {
    $('button#hotfix_' + id).hide();
    $('span#hotfix_error_' + id).html('');
  }
});

$('select#common_select').change(function() {
  var selected_version = $('select#common_select option:selected').val();
  var ignored = $('.version option[value="ignore"]' );
  var version = "";
  if(selected_version.match(/^branch/)) {
    version = selected_version.replace(
      /^branch\/(mr[0-9]+\.[0-9]+(\.[0-9]+)?)$/g, "$1");
  }
  else {
    version = selected_version.replace(
      /^tag\/(mr[0-9]+\.[0-9]+\.[0-9]+)(\.[0-9]+)?$/g, "$1");
  }
  // set ignored for all
  ignored.prop('selected', true);
  ignored.each(function(){ $(this).change(); });
  $('tr.repo option[value="ignore"]').closest('tr').children('td,th').css('background-color','#F78181');
  var selected = $('.version option[value="'+ selected_version + '"]' )
  selected.prop('selected', true);
  selected.each(function(){ $(this).change(); });
  $('tr.repo option[value="'+ selected_version + '"]').closest('tr').children('td,th').css('background-color','white');
  var text = "Selected " + selected.length + " of " + ignored.length;
  $('#select_text_info').text(text);
  $('input#version_release').val("release-" + version);
});

$( document ).ready(function() {
  $('td.version > select option[value^="branch/mr"]').each(function(){ $(this).change(); });
});