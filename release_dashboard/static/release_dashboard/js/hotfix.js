/**
 *
 *
 */
$( "button.hotfix" ).click( function( e ) {

  // don't send the form
  e.preventDefault();
  var button = $( this );
  var id = button.attr( "id" ).replace( "hotfix_", "" );
  var branch = $( "select#version_" + id + " option:selected" ).val().replace( "branch/", "" );
  var repo = id;
  var span = $( "span#hotfix_error_" + id );
  var links = $( "#links_" + id );
  var push = $( "select#push_" + id + " option:selected" ).val();
  var empty = $( "input#empty_" + id ).prop( "checked" );

  $.ajax( {
    url: branch + "/" + repo + "/",
    type: "POST",
    data: JSON.stringify( { push: push, empty: empty } ),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: successFunc,
    error: errorFunc,
    /* eslint-disable-next-line no-undef */ // at csrf.js
    beforeSend: csrftokenFunc
  } );

  button.attr( "disabled", "disabled" );
  span.html( "processing" );
  span.show();
  links.addClass( "hidden" );

  function successFunc( data, _status ) {
    span.html( "" );
    $( "#link_done_" + id ).attr( "href", data.urls[ 0 ] );
    $( "#link_latest_" + id ).attr( "href", data.urls[ 1 ] );
    links.removeClass( "hidden" );
    button.removeAttr( "disabled" );
  }

  function errorFunc( _jqXHR, _status, error ) {
    span.html( error );
    button.removeAttr( "disabled" );
  }
} );

$( "td.version > select" ).change( function() {
  var id = $( this ).attr( "id" ).replace( "version_", "" );
  var version = $( this ).val();
  var button = $( "button#hotfix_" + id );
  var span = $( "span#hotfix_error_" + id );
  var links = $( "#links_" + id );

  if ( version.match( /^branch\/mr[0-9]+\.[0-9]+\.[0-9]+$/ ) ) {
    button.html( "Release hotfix" );
    button.removeAttr( "disabled" );
  } else {
    button.html( "Select branch to hotfix" );
    button.attr( "disabled", "disabled" );
  }
  span.html( "" );
  links.addClass( "hidden" );
} );

$( document ).ready( function() {
  $( "td.version > select option[value^=\"branch/mr\"]" ).each( function() {
 $( this ).change();
} );
} );
