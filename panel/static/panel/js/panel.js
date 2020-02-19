/**
 *
 *
 */
 $.release = {
  release_jobs: new Set(),
  projects: new Set(),
  stats: {
    danger: new Set(),
    success: new Set(),
    warning: new Set(),
    created: new Set(),
    queued: new Set()
  },
  interval: 15000
};

/* eslint-disable-next-line no-unused-vars*/ // called in templates
function set_stats_total( value ) {
  var div_stats_total = $( "#stats-total" );
  if ( $.release.uuid ) {
    div_stats_total.text( value );
  }
}

function get_label_status( status ) {
  var result;
  switch ( status ) {
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

function get_class_status( base, status ) {
    return base + get_label_status( status );
}

function set_project_stats( project, label ) {
  var labels = new Set( Object.keys( $.release.stats ) );
  labels.delete( label );

  for ( var item of labels ) {
    if ( $.release.stats[ item ].has( project ) ) {
      $.release.stats[ item ].delete( project );
    }
  }
  create_new_project_stat( project, label );
  if ( $.release.stats[ label ] ) {
    $.release.stats[ label ].add( project );
  }
}

function update_stats_progress() {
  var labels = new Set( Object.keys( $.release.stats ) );
  var total = $.release.projects.size;

  if ( $.release.uuid ) {
    total += $.release.stats.queued.size;
  }

  for ( var label of labels ) {
    var num = ( ( $.release.stats[ label ].size * 100 ) / total ).toPrecision( 3 );
    var div_progress = $( ".progress-bar-" + label );

    div_progress.attr( "aria-valuenow", num );
    div_progress.text( num + "%" ).css( "width", num + "%" );
    $( "#stats-" + label ).text( $.release.stats[ label ].size );
  }
}

function update_stats() {
  for ( var project of $.release.projects ) {
    var div_uuid = $( "#" + project + "-" + $.release[ project ].last_uuid );
    if ( div_uuid.hasClass( "panel-danger" ) ) {
      set_project_stats( project, "danger" );
    } else if ( div_uuid.hasClass( "panel-warning" ) ) {
      set_project_stats( project, "warning" );
    } else if ( div_uuid.hasClass( "panel-success" ) ) {
      set_project_stats( project, "success" );
    } else {
      set_project_stats( project, "created" );
    }
  }
  update_stats_progress();
}

/*******************************************************************/
function showProjectBuild( div_project, value ) {
  if ( !$.release.uuid ) {
    return;
  }
  var div_retrigger = $( ".retrigger-project-url", div_project );
  if ( value ) {
    div_retrigger.removeClass( "hidden" );
  } else {
    div_retrigger.addClass( "hidden" );
  }
}

function set_project_status( project, value ) {
  var div_project = $( "#" + project );
  var div_uuid = $( "#" + project + "-" + $.release[ project ].last_uuid );
  var status;

  if ( value ) {
    if ( value.created ) {
      div_project.removeClass( "panel-warning panel-danger panel-success" );
      showProjectBuild( div_project, false );
      status = "CREATED";
    } else {
      status = value.result;
      div_project.addClass( get_class_status( "panel-", status ) );
    }
  } else {
    if ( div_uuid.hasClass( "panel-warning" ) ) {
      div_project.addClass( "panel-warning" );
      showProjectBuild( div_project, true );
      status = "warning";
    } else if ( div_uuid.hasClass( "panel-danger" ) ) {
      div_project.addClass( "panel-danger" );
      showProjectBuild( div_project, true );
      status = "danger";
    } else if ( div_uuid.hasClass( "panel-success" ) ) {
      div_project.addClass( "panel-success" );
      showProjectBuild( div_project, false );
      status = "success";
    }
  }
  if ( project !== "release-copy-debs-yml" ) {
    update_stats();
  }
}

function set_uuid_status( project, uuid, job, value ) {
  var id = project + "-" + uuid;
  var div_uuid = $( "#" + id );
  var div_uuid_date = $( "#" + id + "-date" );
  var status = value.result;
  var _class = get_class_status( "panel-", status );
  var jobs = $.release[ project ][ uuid ].jobs.size;

  switch ( status ) {
    case "UNSTABLE":
    case "SUCCESS":
      if ( job.match( /.+-repos$/ ) || job === "release-copy-debs-yml" ) {
        div_uuid.removeClass( "panel-warning panel-danger" ).addClass( _class );
        console.debug( project + " uuid: " + uuid + " OK. done" );
      }
      break;
    default:
      if ( job.match( /.+piuparts$/ ) ) {
        div_uuid.addClass( "panel-warning" ).removeClass( "panel-success panel-danger" );
      } else {
        div_uuid.addClass( _class );
        if ( !$.release[ project ][ uuid ].failed ) {
          $.release[ project ][ uuid ].failed = true;
          console.debug( project + " uuid: " + uuid + " set failed" );
        }
      }
  }
  div_uuid_date.text( new Date( value.date ).toUTCString() );
  $( "#" + id + "-badge" ).text( jobs );
  if ( uuid === $.release[ project ].last_uuid ) {
    set_project_status( project );

    // update badge
    $( "#stats-" + project + " > .badge" ).text( jobs );
  }
}

function set_job_status( project, uuid, job, value ) {
  var id = project + "-" + uuid + "-" + job;
  var div_job = $( "#" + id );
  if ( value ) {
    var url = value.job_url + value.buildnumber + "/";
    div_job.addClass( get_class_status( "list-group-item-", value.result ) );
    $( ".link", div_job ).attr( "href", url );
  } else {

    // this should not happend!!
    console.error( job + " not found" );
  }
}

/*******************************************************************/
function create_new_project_stat( project, label ) {
  var id = "stats-" + project;
  if ( $.release.stats[ label ].has( project ) ) {
    return;
  } else {
    $( "#" + id ).remove();
  }
  var div_project = $( ".stats-project-" + label + "-clone" ).clone();
  var jobs = 0;

  div_project.removeClass( "hidden stats-project-" + label + "-clone" );
  div_project.attr( "id", id );

  if ( project in $.release ) {
    var uuid = $.release[ project ].last_uuid;
    if ( uuid ) {
      if ( $.release[ project ][ uuid ] && $.release[ project ][ uuid ].jobs ) {
        jobs = $.release[ project ][ uuid ].jobs.size;
      }
    }
    var div_link = $( ".link", div_project );
    div_link.attr( "href", "#" + project );
    div_link.text( project );
    $( ".badge", div_project ).text( jobs );
  } else {
    div_project.text( project );
      console.debug( project + " on queue" );
  }

  // put it on the proper place
  div_project.appendTo( "#stats-list-" + label );
}

function create_new_job_div( project, uuid, job ) {
  var id = project + "-" + uuid;
  var div_job = $( "#" + id + "-job" ).clone().removeClass( "hidden" );

  div_job.attr( "id", id + "-" + job );
  $( ".link", div_job ).text( job );
  div_job.appendTo( "#" + id + "-list" );
}

/**
 * The idea is to have a hidden blocks to clone
 * be sure to create proper ids and remove the classes
 * you use to select them
 */
function create_new_uuid_panel( project, uuid ) {
  var id = project + "-" + uuid;
  var div_uuid = $( "#" + project + " > .panel-body .uuid-clone" ).clone();
  var uuid_url;
  div_uuid.removeClass( "hidden" );
  div_uuid.attr( "id", id ).removeClass( "uuid-clone" ).addClass( "uuid" );

  // rest of blocks or classes to select inside this
  $( ".uuid-list", div_uuid ).attr( "id", id + "-list" ).removeClass( "uuid-list" );
  $( ".job", div_uuid ).attr( "id", id + "-job" ).removeClass( "job" );

  var div_title = $( ".panel-heading > .panel-title", div_uuid );
  var div_uuid_name = $( ".uuid-name", div_title );
  div_uuid_name.attr( "id", id + "-name" ).removeClass( "uuid-name" );
  if ( $.release.uuid ) {
    div_uuid_name.replaceWith( uuid );
  } else {
    if ( $.panel === "project_uuid" ) {
      uuid_url = "#";
    } else if ( $.panel === "release" ) {
      uuid_url = project + "/" + uuid;
    } else {
      uuid_url = uuid;
    }
    div_uuid_name.attr( "name", id );
    div_uuid_name.attr( "href", uuid_url );
    div_uuid_name.text( uuid );
  }
  var div_uuid_date = $( ".uuid-date", div_title ).attr( "id", id + "-date" );
  div_uuid_date.removeClass( "uuid-date" );
  div_uuid_date.text( "date" );
  var div_uuid_badge = $( ".uuid-badge", div_title ).attr( "id", id + "-badge" );
  div_uuid_badge.removeClass( "uuid-badge" );
  div_uuid_badge.text( $.release[ project ][ uuid ].jobs.size );

  // put it on the proper place
  div_uuid.prependTo( "#" + project + " > .panel-body" );
  console.debug( "uuid " + uuid + " created for " + project );
}

function create_new_project_panel( project ) {
  var div_project = $( ".project-clone" ).clone();
  var div_stats_total = $( "#stats-total" );
  if ( !$.release.uuid ) {
    div_stats_total.text( $.release.projects.size );
  }
  div_project.removeClass( "hidden" );
  div_project.attr( "id", project ).removeClass( "project-clone" ).addClass( "project" );

  var div_title = $( ".project-name", div_project );
  if ( $.release.uuid ) {
    div_title.text( project );
    $( ".latest-uuid-url", div_project ).addClass( "hidden" );
  } else {
    var div_title_link = $( ".link", div_title );
    div_title_link.attr( "name", project );
    div_title_link.attr( "href", "./" + project + "/" );
    div_title_link.text( project );

    var latest_uuid_url;
    if ( $.panel === "project_uuid" ) {
      latest_uuid_url = "../latest/";
    } else if ( $.panel === "release" ) {
      latest_uuid_url = project + "/latest/";
    } else {
      latest_uuid_url = "latest/";
    }
    $( ".latest-uuid-url", div_project ).attr( "href", latest_uuid_url );
  }
  $( ".error", div_project ).attr( "id", project + "-error" ).removeClass( "error" );
  div_project.appendTo( "#project-list" );
  console.debug( "project " + project + " created" );
}

/******************************************************************/
function create_new_job( project, uuid, data ) {
  if ( !data ) {
    console.debug( "project:" + project + " uuid:" + uuid + " has no data" );
  }
  var job = data.jobname;
  if ( $.release[ project ][ uuid ] == null ||
     $.release[ project ][ uuid ].jobs.has( job ) ) {
    console.debug( "project " + project + " has no uuid:" + uuid );
    return;
  }

  $.release[ project ][ uuid ].jobs.add( job );
  $.release[ project ][ uuid ][ job ] = { failed: false };
  create_new_job_div( project, uuid, job );
  set_job_status( project, uuid, job, data );
  set_uuid_status( project, uuid, job, data );
}

function clean_uuids( project ) {
  if ( $.release.max_uuids === 0 ) {
    return;
  }
  if ( $.release[ project ].uuids.size > $.release.max_uuids ) {
    var step = $.release[ project ].uuids.size - $.release.max_uuids;
    for ( var uuid of $.release[ project ].uuids ) {
      if ( step === 0 ) {
        return;
      }
      if ( uuid !== $.release[ project ].last_uuid ) {
        $( "#" + project + "-" + uuid ).remove();
        $.release[ project ].uuids.delete( uuid );
        console.debug( "project " + project + " " + uuid + " removed" );
        $.release[ project ].removed_uuids.add( uuid );
        step--;
      }
    }
  }
}

function create_new_uuid( release, project, values, update = true ) {
  var uuid = values.tag;
  if ( uuid == null || $.release[ project ].uuids.has( uuid ) ) {
    return;
  }

  // no need to add to remove later
  if ( !values.latest &&
      $.release[ project ].uuids.size > $.release.max_uuids ) {
    return;
  }

  $.release[ project ].uuids.add( uuid );
  $.release[ project ][ uuid ] = { failed: false, jobs: new Set() };

  create_new_uuid_panel( project, uuid );
  if ( update ) {
    update_uuid_info( release, project, uuid );
  } else {
    if ( values.latest ) {
      $.release[ project ].last_uuid = uuid;
      showLatestUUID( project, uuid );
    }
  }
  set_project_status( project, { created: true } );
}

function create_new_project( release, project, update = true ) {
  if ( $.release.projects.has( project ) ) {
    return;
  }

  $.release.projects.add( project );
  $.release[ project ] = { uuids: new Set(), failed: false,
    interval: 5000, last_uuid: null, removed_uuids: new Set() };
  create_new_project_panel( project );

  if ( update ) {
    get_uuids_for_project( release, project );
  }
}

/* eslint-disable-next-line no-unused-vars*/ // used at onClick
function retrigger_project( project ) {
  var div_project = $( "#" + project );

  function successFunc( _data, _textStatus, _jqXHR ) {
    showProjectBuild( div_project, false );
    $( "#" + project + "-error" ).text();
  }

  function errorFunc( _jqXHR, _status, error ) {
    $( "#" + project + "-error" ).text( error );
  }
  var url = "/build/" + $.release.uuid + "/" + project + "/?format=json";
  $.ajax( {
    url: url,
    method: "GET",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  } );
}

/******************************************************************/

function update_uuid_info( release, project, uuid ) {

  function successFunc( data, _textStatus, _jqXHR ) {
    $( data ).each( function() {
      if ( !$.release[ project ][ uuid ].jobs.has( this.jobname ) ) {
        create_new_job( project, uuid, this );
      }
    } );
  }

  function errorFunc( _jqXHR, _status, error ) {
    $( "#" + project + "-error" ).text( error );
    $.release[ project ][ uuid ].failed = true;
  }

  var url = "/release/" + release + "/" + project + "/" + uuid + "/?format=json";
  if ( $.release.uuid ) {
    url += "&release_uuid=" + $.release.uuid;
  }
  if ( !$.release[ project ][ uuid ].failed ) {
    $.ajax( {
      url: url,
      method: "GET",
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: successFunc,
      error: errorFunc
    } );
  }
}

function showLatestUUID( project, uuid ) {
  var div_project = $( "#" + project );
  $( ".uuid-latest", project ).addClass( "hidden" );
  var div_uuid_name = $( "#" + project + "-" + uuid );
  $( ".uuid-latest", div_uuid_name ).removeClass( "hidden" );
  var div_retrigger_btn = $( ".retrigger-project-url", div_project );
  div_retrigger_btn.attr( "onclick", "retrigger_project(\"" + project + "\")" );
}

function get_uuids_for_project( release, project ) {

  function successFunc( data, _textStatus, _jqXHR ) {
    $( data ).each( function() {
      if ( $.release[ project ].removed_uuids.has( this.tag ) ) {

        /* skip iteration */
        return true;
      }
      if ( this.latest && $.release[ project ].last_uuid !== this.tag ) {
        $.release[ project ].last_uuid = this.tag;
        console.debug( project + ".latest_uuid:" + $.release[ project ].last_uuid );
      }
      if ( !$.release[ project ].uuids.has( this.tag ) ) {
          create_new_uuid( release, project, this );
      } else if ( !$.release[ project ][ this.tag ].failed ) {
        update_uuid_info( release, project, this.tag );
      }
      if ( this.latest ) {
        showLatestUUID( project, this.tag );
      }
    } );
    clean_uuids( project );
  }

  function errorFunc( _jqXHR, _status, error ) {
    $( "#" + project + "-error" ).text( error );
  }
  var url = "/release/" + release + "/" + project + "/?format=json";
  if ( $.release.uuid ) {
    url += "&release_uuid=" + $.release.uuid;
  }
  $.ajax( {
    url: url,
    method: "GET",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  } );
}

function get_projects( release ) {

  function successFunc( data, _textStatus, _jqXHR ) {
    $( data ).each( function() {
      if ( !$.release.projects.has( this.projectname ) ) {
        create_new_project( release, this.projectname );
      }
    } );
  }

  function errorFunc( _jqXHR, _status, error ) {
    console.error( error );
  }

  var url = "/release/" + release + "/?format=json";
  if ( $.release.uuid ) {
    url += "&release_uuid=" + $.release.uuid;
  }
  $.ajax( {
    url: url,
    method: "GET",
    async: false,
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  } );
}

/* eslint-disable-next-line no-unused-vars*/ // used on templates
function update_info( release ) {
  if ( $.release.uuid ) {
    /* eslint-disable-next-line no-undef */
    get_release_jobs();
  }
  get_projects( release );
  for ( var project of $.release.projects ) {
    get_uuids_for_project( release, project );
  }
}
