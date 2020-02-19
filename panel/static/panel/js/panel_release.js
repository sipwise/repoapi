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
  div_job.html( "<a href=\"" + data.url + "\">" + job + "</a>" );
}

/* eslint-disable-next-line no-unused-vars*/ // used on templates
function get_release_jobs() {

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

  var url = "/release_jobs/" + $.release.uuid + "/?format=json";
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
