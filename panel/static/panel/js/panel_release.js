/* eslint-disable-next-line no-unused-vars*/ // used at onClick
function click_retrigger( e, project ) {
    retrigger_project( project );
    e.preventDefault();
}

/* eslint-disable-next-line no-unused-vars*/ // used at onClick
function click_build( e, project ) {
  var div_project = $( "#stats-" + project );
  if ( $.release.release_jobs.size < $.release.release_jobs_size ) {
    alert( "Not all release_jobs are done, builds are not allowed" );
  } else {
    var ok = confirm( "This will build " + project + ", are you sure?" );
    if ( ok === true ) {
      div_project.text( project );
      build_queued_project( project );
    }
  }
  e.preventDefault();
}

/* eslint-disable-next-line no-unused-vars*/ // used at onClick
function click_resume( e, id ) {
    resume_build( id );
    e.preventDefault();
}

function resume_build( id ) {

  function successFunc( _data, _textStatus, _jqXHR ) {
    $( "#resume" ).prop( "disabled", true );
  }

  function errorFunc( _jqXHR, _status, error ) {
    $( "#release_error" ).html( error );
  }
  var csrftoken = jQuery( "[name=csrfmiddlewaretoken]" ).val();
  function csrfSafeMethod( method ) {

    // these HTTP methods do not require CSRF protection
    return ( /^(GET|HEAD|OPTIONS|TRACE)$/.test( method ) );
  }
  $.ajaxSetup( {
    beforeSend: function( xhr, settings ) {
        if ( !csrfSafeMethod( settings.type ) && !this.crossDomain ) {
            xhr.setRequestHeader( "X-CSRFToken", csrftoken );
        }
    }
  } );
  $.ajax( {
    url: "/build/" + id + "/?format=json",
    data: JSON.stringify( { action: "resume" } ),
    method: "PATCH",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  } );
}

function clean_all_uuids( project ) {
  for ( var uuid of $.release[ project ].uuids ) {
    $( "#" + project + "-" + uuid ).remove();
    $.release[ project ].uuids.delete( uuid );
    console.debug( "project " + project + " " + uuid + " removed" );
    $.release[ project ].removed_uuids.add( uuid );
  }
  $.release[ project ].last_uuid = null;
}

function retrigger_project( project ) {

  function successFunc( _data, _textStatus, _jqXHR ) {
    clean_all_uuids( project );
    /* eslint-disable-next-line no-undef */ // on panel.js
    set_project_status( project, { created: true } );
    $( "#" + project + "-error" ).text();
  }

  function errorFunc( _jqXHR, _status, error ) {
    $( "#" + project + "-error" ).text( error );
  }
  var csrftoken = jQuery( "[name=csrfmiddlewaretoken]" ).val();
  function csrfSafeMethod( method ) {

    // these HTTP methods do not require CSRF protection
    return ( /^(GET|HEAD|OPTIONS|TRACE)$/.test( method ) );
  }
  $.ajaxSetup( {
    beforeSend: function( xhr, settings ) {
        if ( !csrfSafeMethod( settings.type ) && !this.crossDomain ) {
            xhr.setRequestHeader( "X-CSRFToken", csrftoken );
        }
    }
  } );
  var url = "/build/" + $.release.uuid + "/" + project + "/?format=json";
  $.ajax( {
    async: true,
    url: url,
    method: "POST",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  } );
}

function build_queued_project( project ) {

  function successFunc( _data, _textStatus, _jqXHR ) {
    console.debug( "build sent for " + project );
  }

  function errorFunc( _jqXHR, _status, error ) {
    console.error( error );
  }
  var csrftoken = jQuery( "[name=csrfmiddlewaretoken]" ).val();
  function csrfSafeMethod( method ) {

    // these HTTP methods do not require CSRF protection
    return ( /^(GET|HEAD|OPTIONS|TRACE)$/.test( method ) );
  }
  $.ajaxSetup( {
    beforeSend: function( xhr, settings ) {
        if ( !csrfSafeMethod( settings.type ) && !this.crossDomain ) {
            xhr.setRequestHeader( "X-CSRFToken", csrftoken );
        }
    }
  } );
  var url = "/build/" + $.release.uuid + "/" + project + "/?format=json";
  $.ajax( {
    async: true,
    url: url,
    method: "POST",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  } );
}

function create_new_release_job( data ) {
  var job = data.jobname;
  if ( $.release.release_jobs.has( job ) ) {
    return;
  }

  $.release.release_jobs.add( job );
  $.release[ job ] = { uuids: new Set(), failed: false,
    interval: 5000, last_uuid: null, removed_uuids: new Set() };

  var div_job = $( ".clone-release-job" ).clone();
  div_job.removeClass( "hidden clone-release-job" );
  div_job.attr( "id", job );
  div_job.html( "<a href=\"" + data.job_url + data.buildnumber + "\">" + job + "</a>" );
  /* eslint-disable-next-line no-undef */ //defined at panel.js file
  div_job.addClass( get_class_status( "list-group-item-", data.result ) );
  div_job.appendTo( "#release-job-list" );
}

function get_release_jobs_info( job ) {

  function successFunc( data, _textStatus, _jqXHR ) {
    $( data ).each( function() {
      if ( !$.release.release_jobs.has( this.jobname ) ) {
        create_new_release_job( this );
      }
    } );
  }

  function errorFunc( _jqXHR, _status, error ) {
    console.error( error );
  }

  var url = "/release_jobs/" + $.release.uuid + "/" + job + "/?format=json";
  $.ajax( {
    async: true,
    url: url,
    method: "GET",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  } );
}

/* eslint-disable-next-line no-unused-vars */ // used on templates
function get_release_jobs() {

  function successFunc( data, _textStatus, _jqXHR ) {
    $( data ).each( function() {
      get_release_jobs_info( this );
    } );
  }

  function errorFunc( _jqXHR, _status, error ) {
    console.error( error );
  }

  var url = "/release_jobs/" + $.release.uuid + "/?format=json";
  $.ajax( {
    async: true,
    url: url,
    method: "GET",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc
  } );
}

/* we can't use $.release[ project ][ uuid ].failed value
 * since we can have child jobs that fail and parent can
 * ignore them and keep the flow
 *
 */
function is_project_done( project ) {
  var uuid = $.release[ project ].last_uuid;
  if ( uuid === null ) {
    return false;
  }
  return $.release[ project ][ uuid ].jobs.has( project + "-repos" );
}


function is_done() {
  var success = parseInt( $( "#stats-success" ).text(), 10 );
  var failed = parseInt( $( "#stats-danger" ).text(), 10 );
  var queued = parseInt( $( "#stats-queued" ).text(), 10 );
  var building = parseInt( $( "#stats-created" ).text(), 10 );

  if ( failed === 0 && queued === 0 && building === 0 && success > 0 ) {
    return true;
  }
  return false;
}

function is_stuck() {
  var success = parseInt( $( "#stats-success" ).text(), 10 );
  var failed = parseInt( $( "#stats-danger" ).text(), 10 );
  var queued = parseInt( $( "#stats-queued" ).text(), 10 );
  var building = parseInt( $( "#stats-created" ).text(), 10 );

  if ( failed === 0 && queued > 0 && building === 0 && success > 0 ) {
    return true;
  }
  return false;
}

/* eslint-disable-next-line no-unused-vars */ // used on templates
function update_release_info( release ) {
  if ( $.release.release_jobs.size < $.release.release_jobs_size ) {
    get_release_jobs();
  }
  /* eslint-disable-next-line no-undef */ // on panel.js
  get_projects( release );
  for ( var project of $.release.projects ) {
    if ( !is_project_done( project ) ) {
      /* eslint-disable-next-line no-undef */ // on panel.js
      get_uuids_for_project( release, project );
    }
  }
  if ( is_done() ) {
    clearInterval( $.release.timer );
    clearInterval( $.release.update_info_timer );
    $( "#update-info-all" ).addClass( "hidden" );
    $( "#resume" ).prop( "disabled", true );
  } else if ( is_stuck() ) {
    $( "#resume" ).prop( "disabled", false );
  }
}
