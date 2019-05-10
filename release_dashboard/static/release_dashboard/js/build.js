/**
 *
 */
$('select#common_select').change(function() {
  var selected_version = $('select#common_select option:selected').val();
  var ignored = $('.version option[value="ignore"]' );
  var version = "";
  if(selected_version.match(/^branch/)) {
    if(selected_version.match(/^branch\/master/)) {
      var distribution = $('select#distribution option:selected').val();
      if(distribution && !distribution.match(/^auto/)) {
        version = 'trunk' + '-' + distribution;
      }
    }
    else {
      version = selected_version.replace(
        /^branch\/(mr[0-9]+\.[0-9]+(\.[0-9]+)?)$/g, "$1");
    }
  }
  else if(selected_version.match(/^tag/)) {
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
  $('#select_text_info').html(text);
  if(version.length > 0) {
    $('input#version_release').val("release-" + version);
  } else {
    $('input#version_release').val('none');
  }
});

$('#main').click(function(e){
  var version = $('#version_release');
  if (version.val().length == 0) {
    alert("release version empty");
    version.focus();
    // don't send the form
    e.preventDefault();
  }
});

$( document ).ready(function() {
  var common_select = $('select#common_select option:selected');
  var value = common_select.val();
  if (value != 'ignore') {
    common_select.change();
  }
});

function click_ignore(e) {
    var selection_box_id = e.target.id.split('_')[1];
    var selection_box = $('#version_' + selection_box_id);
    selection_box.val('ignore');
    e.preventDefault();
}
