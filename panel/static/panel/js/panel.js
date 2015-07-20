/**
 *
 *
 */
 $.release = {
  projects: new Set(),
  stats: {
    danger: new Set(),
    success: new Set(),
    warning: new Set(),
    created: new Set(),
  },
  interval: 15000,
};

function get_label_status(status) {
  var result;
  switch (status) {
    case "SUCCESS":
      result = "success";
      break;
    case "UNSTABLE":
      result = "warning";
      break;
    case "CREATED":
      result = "default";
      break;
    default:
      result = "danger";
  }
  return result;
}

function get_class_status(base, status) {
    return base + get_label_status(status);
}

function sort_project_stat_lists() {
  $('.list-stat').each(function() {
    $(this).children().detach().sort(function(a, b) {
      return $(a).text().localeCompare($(b).text());
    }).appendTo(this);
  });
}

function set_project_stats(project, label)
{
  var labels = new Set(Object.keys($.release.stats));
  labels.delete(label);

  for (var item of labels) {
    if ($.release.stats[item].has(project)) {
      $.release.stats[item].delete(project);
    }
  }
  create_new_project_stat(project, label);
  if($.release.stats[label]) {
    $.release.stats[label].add(project);
  }
  sort_project_stat_lists();
}

function update_stats_progress() {
  var labels = new Set(Object.keys($.release.stats));
  var total = $.release.projects.size;

  for (var label of labels) {
    var num = (($.release.stats[label].size * 100)/total).toPrecision(3);
    var div_progress = $('.progress-bar-' + label);

    div_progress.attr('aria-valuenow', num);
    div_progress.html( num + '%').css('width', num + '%');
    $('#stats-' + label).html($.release.stats[label].size);
  }
}

function update_stats() {
  for (var project of $.release.projects) {
    var div_uuid = $('#'+ project + '-' + $.release[project].last_uuid);
    if (div_uuid.hasClass('panel-danger')) {
      set_project_stats(project, 'danger');
    }
    else if (div_uuid.hasClass('panel-warning')) {
      set_project_stats(project, 'warning');
    }
    else if (div_uuid.hasClass('panel-success')) {
      set_project_stats(project, 'success');
    }
    else {
      set_project_stats(project, 'created');
    }
  }
  update_stats_progress();
}

/*******************************************************************/
function set_project_status(project, value) {
  var div_project = $('#' + project);
  var div_uuid = $('#'+ project + '-' + $.release[project].last_uuid);
  var status;

  if (value) {
    if(value.created) {
      div_project.removeClass('panel-warning panel-danger panel-success');
      status = "CREATED";
    }
    else {
      status = value.result;
      div_project.addClass(get_class_status("panel-", status));
    }
  }
  else {
    if (div_uuid.hasClass('panel-warning')) {
      div_project.addClass('panel-warning');
      status = 'warning';
    }
    else if (div_uuid.hasClass('panel-danger')) {
      div_project.addClass('panel-danger');
      status = 'danger';
    }
    else if (div_uuid.hasClass('panel-success')) {
      div_project.addClass('panel-success');
      status = 'success';
    }
  }
  update_stats();
}

function set_uuid_status(project, uuid, job, value) {
  var div_uuid = $('#' + project + '-' + uuid);
  var status = value.result;
  var _class = get_class_status("panel-", status);
  var jobs = $.release[project][uuid].jobs.size;

  switch (status) {
    case "UNSTABLE":
    case "SUCCESS":
      if (job.match(/.+-repos$/)) {
        div_uuid.removeClass('panel-warning panel-danger').addClass(_class);
        console.debug(project + ' uuid: ' + uuid + " OK. done");
      }
      break;
    default:
      if (job.match(/.+piuparts$/)) {
        div_uuid.addClass('panel-warning').removeClass('panel-success panel-danger');
      }
      else {
        div_uuid.addClass(_class);
        if(! $.release[project][uuid].failed) {
          $.release[project][uuid].failed = true;
          console.debug(project + ' uuid: ' + uuid + ' set failed');
        }
      }
  }
  $('.badge', div_uuid).html(jobs);
  if (uuid == $.release[project].last_uuid) {
    set_project_status(project);
    // update badge
    $('#stats-' + project + ' > .badge').html(jobs);
  }
}

function set_job_status(project, uuid, job, value) {
  var id = project + '-' + uuid + '-' + job;
  var div_job = $('#' + id);

  if (value) {
    console.debug(job + ' found');
    div_job.addClass(get_class_status("list-group-item-", value.result));
    div_job.html('<a href="' + value.job_url + value.buildnumber
      + '">' + job + '</a>');
  }
  else {
    console.error(job + ' not found');
    // this should not happend!!
  }
}

/*******************************************************************/
function create_new_project_stat(project, label) {
  var id = 'stats-' + project;
  var uuid = $.release[project].last_uuid;
  if ( $.release.stats[label].has(project) ) { return; }
  else { $('#' + id).remove(); }
  var div_project = $('.stats-project-' + label + '-clone').clone();
  var jobs = 0;

  div_project.removeClass('hidden stats-project-' + label + '-clone');

  if( $.release[project][uuid] && $.release[project][uuid].jobs) {
    jobs = $.release[project][uuid].jobs.size;
  }
  div_project.attr('id', id);
  div_project.html('<a href="#' + project +'"/">' + project +
    ' <span class="badge">' + jobs + '</span></a>');

  // put it on the proper place
  div_project.appendTo('#stats-list-' + label);
}

function create_new_job_div(project, uuid, job) {
  var id = project + '-' + uuid;
  var div_job = $('#' + id + '-job').clone().removeClass('hidden');

  div_job.attr('id', id + '-' + job).html(job);
  // put it on the proper place
  div_job.appendTo('#' + id + '-list');
  console.debug('job ' + job + ' created for ' + project + ' uuid: ' + uuid);
}

/**
 * The idea is to have a hidden blocks to clone
 * be sure to create proper ids and remove the classes
 * you use to select them
 */
function create_new_uuid_panel(project, uuid) {
  var id = project + '-' + uuid;
  var div_uuid = $('#' + project +' > .panel-body .uuid-clone').clone();
  div_uuid.removeClass('hidden');
  div_uuid.attr('id', id).removeClass('uuid-clone').addClass('uuid');

  // rest of blocks or classes to select inside this
  $('.uuid-list', div_uuid).attr('id', id + '-list').removeClass('uuid-list');
  $('.job', div_uuid).attr('id', id + '-job').removeClass('job');

  var div_title = $('.panel-heading > .panel-title', div_uuid);
  div_title.html('<a name="' + id +'"/">' + uuid +
    ' <span class="badge">' + $.release[project][uuid].jobs.size + '</span></a>');

  // put it on the proper place
  div_uuid.prependTo('#' + project + ' > .panel-body');
  console.debug('uuid ' + uuid + ' created for ' + project);
}

function create_new_project_panel(project) {
  var div_project = $('.project-clone').clone();
  var div_stats_total = $('#stats-total').html($.release.projects.size);
  div_project.removeClass('hidden');
  div_project.attr('id', project).removeClass('project-clone').addClass('project');

  var div_title = $('.panel-heading > .panel-title', div_project);
  div_title.html('<a name="' + project +'" href="./' + project + '/">' + project + '</a>');

  $('.error', div_project).attr('id', project + '-error').removeClass('error');
  div_project.appendTo('#project-list');
  console.debug('project ' + project + ' created');
}
/******************************************************************/
function create_new_job(release, project, uuid, job) {
  if($.release[project][uuid].jobs.has(job)) { return; }

  $.release[project][uuid].jobs.add(job);
  $.release[project][uuid][job] = { failed: false, };
  create_new_job_div(project, uuid, job);
  update_job_info(release, project, uuid, job);
}

function clean_uuids(release, project) {
  if ($.release.max_uuids == 0) { return; }
  if ($.release[project].uuids.size >= $.release.max_uuids) {
    var step = $.release[project].uuids.size - $.release.max_uuids;
    for (var uuid of $.release[project].uuids) {
      if (step==0) { return; }
      console.debug(uuid);
      if (uuid != $.release[project].last_uuid)
      {
        $('#' + project + '-' + uuid).remove();
        step--;
      }
    }
  }
}

function create_new_uuid(release, project, uuid) {
  if (uuid == null || $.release[project].uuids.has(uuid)) {
    return;
  }

  $.release[project].uuids.add(uuid);
  $.release[project].last_uuid = uuid;
  $.release[project][uuid] = { failed: false, jobs: new Set(),};

  clean_uuids(release, project);
  create_new_uuid_panel(project, uuid);
  update_uuid_info(release, project, uuid);
  set_project_status(project, {created: true});
}

function create_new_project(release, project) {
  if ($.release.projects.has(project)) {
    return;
  }
  $.release.projects.add(project);
  $.release[project] = {uuids: new Set(), failed: false, interval: 5000,};
  create_new_project_panel(project);

  get_uuids_for_project(release, project);
}

/******************************************************************/

function update_job_view(project, uuid, job, data) {
  var value = data.results[0];

  if (data.count != 0) {
    set_job_status(project, uuid, job, value);
    set_uuid_status(project, uuid, job, value);
  }
  else {
    console.error(job + ' not found');
    // this should not happend!!
  }
}

function update_job_info(release, project, uuid, job) {

  function successFunc(data, textStatus, jqXHR ) {
    update_job_view(project, uuid, job, data);
  }

  function errorFunc(jqXHR, status, error) {
    $('#' + project + '-error').html(error);
    $.release[project][uuid][job].failed = true;
  }

  $.ajax({
    url: '/jenkinsbuildinfo/?format=json&tag=' + uuid
      + '&param_release=' + release + '&jobname=' + job,
    method: 'GET',
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  });
}

function update_uuid_info(release, project, uuid) {

  function successFunc(data, textStatus, jqXHR ) {
    $(data).each(function() {
      if (!$.release[project][uuid].jobs.has(this.jobname)) {
        create_new_job(release, project, uuid, this.jobname);
      }
    });
  }

  function errorFunc(jqXHR, status, error) {
    $('#' + project + '-error').html(error);
    $.release[project][uuid].failed = true;
  }

  if (!$.release[project][uuid].failed) {
    $.ajax({
      url: '/uuid/' + release + '/' + project + '/' + uuid + '/?format=json',
      method: 'GET',
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: successFunc,
      error: errorFunc
    });
  }
}

function get_uuids_for_project(release, project) {

  function successFunc(data, textStatus, jqXHR ) {
    $(data).each(function() {
      if (!$.release[project].uuids.has(this.tag)) {
        create_new_uuid(release, project, this.tag);
      }
      else if (!$.release[project][this.tag].failed) {
        update_uuid_info(release, project, this.tag);
      }
    });
  }

  function errorFunc(jqXHR, status, error) {
    $('#' + project + '-error').html(error);
  }

  $.ajax({
    url: '/project/' + release +'/' + project + '/?format=json',
    method: 'GET',
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  });
}

function get_projects(release) {

  function successFunc(data, textStatus, jqXHR ) {
    $(data).each(function() {
      if (!$.release.projects.has(this.projectname)) {
        create_new_project(release, this.projectname);
      }
    });
  }

  function errorFunc(jqXHR, status, error) {
    console.error(error);
  }

  $.ajax({
    url: '/release/' + release + '/?format=json',
    method: 'GET',
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  });
}

function update_info(release) {
  get_projects(release);
  for (var project of $.release.projects) {
    get_uuids_for_project(release, project);
  }
}