/**
 *
 */
$('select.select-version').change(function() {
  var project = $(this).attr('project');
  var selected_version = $(this).val();
  var docker_tag = "latest";

  // clean previous
  $('#docker_tag_' + project).empty();

  if(selected_version == "ignore") {
    get_tags_for_project(project, null);
  } else {
    if(!selected_version.match(/^branch\/master/)) {
      docker_tag = selected_version.replace(
        /^branch\/(mr[0-9]+\.[0-9]+(\.[0-9]+)?)$/g, "$1");
    }
    get_tags_for_project(project, docker_tag);
  }
});


function new_image(project, tag, data) {
  function new_label(image, type, label_text) {
    image.append('<span class="list-group-item list-group-item-' +
      type +'">' + label_text + '</span>');
  }

  var image = $('#docker_image').clone().removeClass('hidden');
  image.attr('id', '#docker_image_' + data.name);
  image.appendTo('#docker_tag_' + project);
  new_label(image, 'success', data.name);

  if (tag) {
    if ($.inArray(tag, data.tags) >= 0) {
      new_label(image, 'info', tag);
    }
  } else {
    data.tags.forEach(function(item) {
      if(item.length > 20) {
        // gerrit review id
        short = item.slice(0,5) + '..' + item.slice(-5);
        new_label(image, 'warning', short);
      } else {
        new_label(image, 'info', item);
      }
    });
  }
}

function get_tags_for_project(project, tag) {

  function successFunc(data, textStatus, jqXHR ) {
    // clean previous
    $('#docker_tag_' + project).empty();
    $(data).each(function() {
      new_image(project, tag, this);
    });
  }

  function errorFunc(jqXHR, status, error) {
    $('#docker_tag_'+project).html();
  }

  $.ajax({
    url: '/docker/' + project + '/?format=json',
    method: 'GET',
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  });
}

$('#docker').click(function(e){
  var common_select = $('select#common_select option:selected');
  common_select.change();
  e.preventDefault();
});
