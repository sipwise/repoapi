/**
 *
 */
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
