// Info window
var infowindow = new google.maps.InfoWindow();

/**
 *  Initializes the Google Map
 */
function initialize_map() {

  // Map options
  var mapOptions = {
      center: new google.maps.LatLng(lat, lon),
      zoom: 10,
      mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  // Draw map
  map = new google.maps.Map(document.getElementById("parkmap"),
                            mapOptions);
};

/**
 *  Draws the markers and boundaries
 */
function draw_markers(){
  // Draw boundaries
  draw_boundaries(boundaries);

  // Draw center markers
  if((show == 'cen' || show == 'all')){
    draw_cenmarkers(cenmarkers);
  }

  // Draw individual markers
  if((show == 'ind' || show == 'all')){
    draw_indmarkers(indmarkers);
  }

  console.log(markers.length);
  // Pan to center if no markers
  if(markers.length == 0){
    map.panTo(center);
  }
  else{
    map.fitBounds(markerBounds);
  }
};

/**
 *  Returns info box for markers
 */
function getInfoCallback(map, content) {
    return function() {
            infowindow.close();
            infowindow.setContent(content);
            infowindow.open(map, this);
        };
};

/**
 *  Draws boundaries for the park
 */
function draw_boundaries(boundaries){

  var parkpath = [];

  for (i = 0; i < boundaries.length; i++) {
    parkpath[i] = new google.maps.Polyline({
      path: boundaries[i],
      geodesic: true,
      strokeColor: '#FF6600',
      strokeOpacity: 1.0,
      strokeWeight: 1
    });
    parkpath[i].setMap(map);
  }
};

/**
 *  Draws individual markers for the park
 */
function draw_indmarkers(inds){

  var marker_i = [];
  for(i = 0; i < inds.length; i++){
    var Position = new google.maps.LatLng(inds[i].latitude,
                                          inds[i].longitude);
    marker_i[i] = new google.maps.Marker({
      position: Position,
      map: map,
      icon: inds[i].marker
    });
    markers.push(marker_i[i]);
    markerBounds.extend(Position);

  // Infobox html
    // Image
    var html = "<img src=" + inds[i].square_link + "><br><br>";
    html += "<span class='text-muted'>";
    // Cluster name
    html += "<span class='markertext'>Cluster:</span> " +
            inds[i].cluster + "<br>";
    // Latitude and Longitude
    html += "<span class='markertext'>Latitude:</span> " +
            inds[i].latitude.toFixed(2) + " <br>";
    html += "<span class='markertext'>Longitude:</span> " +
            inds[i].longitude.toFixed(2) + " <br>";
    // In park
    html += "<span class='markertext'>Core Point:</span> " +
            inds[i].core + " <br>";
    html += "</span>";

    google.maps.event.addListener(marker_i[i], 'click',
      getInfoCallback(map, html));
  }
};

/**
 *  Creates marker listeners
 */
function listener(marker){
  google.maps.event.addListener(marker, 'click', function(){
    document.getElementById("clusterid").innerHTML = "Scene " + marker.cluster;
    document.getElementById("autotags").innerHTML = marker.toptags;
    document.getElementById("similarto").innerHTML = "Similar";
    document.getElementById("similars").innerHTML = marker.similar;
    primeCarousel(marker.label);
  });
};

/**
 *  Draws cluster center markers for park
 */
function draw_cenmarkers(cens){

  var marker_c = [];

  for(i = 0; i < cens.length; i++){
    var Position = new google.maps.LatLng(cens[i].latitude,
                                          cens[i].longitude);
    marker_c[i] = new google.maps.Marker({
      position: Position,
      map: map,
      icon: cens[i].marker,
    });
    markers.push(marker_c[i]);
    markerBounds.extend(Position);

  // Infobox html
    var html = "<span class='text-muted'>";
    // Cluster name
    html += "<span class='markerhead'>Scene " +
            cens[i].cluster + "</span><br><br>";
    // Latitude and Longitude
    html += "<span class='markertext'>Latitude:</span> " +
            cens[i].latitude.toFixed(2) + " <br>";
    html += "<span class='markertext'>Longitude:</span> " +
            cens[i].longitude.toFixed(2) + " <br>";
    // Number of photos and users
    html += "<span class='markertext'># Photos:</span> " +
            cens[i].nophotos + " <br>";
    html += "<span class='markertext'># Users:</span> " +
            cens[i].nousers + " <br>";
    html += "</span>"

    google.maps.event.addListener(marker_c[i], 'click',
      getInfoCallback(map, html));

  // Adding marker listener
    // Cluster info
    marker_c[i].cluster = cens[i].cluster;
    marker_c[i].label = cens[i].label;

    // Top tags
    marker_c[i].toptags = '';
    cens[i].toptags.forEach(function(a){
      a[0] = a[0].charAt(0).toUpperCase() + a[0].slice(1);
      tag = "<b>" + a[0] + "</b>&nbsp;&nbsp;" + a[1] + "<br>";
      marker_c[i].toptags += tag;
    });

    // Scene similarities
    marker_c[i].similar = '';
    cens[i].similar.forEach(function(a){
      tag = "<a class='simscene' id='" + a[0] + "'>Scene " +
            a[0] + "</a>&nbsp;&nbsp;" + a[1] + "%<br>";
      marker_c[i].similar += tag;
    });

    listener(marker_c[i]);

  }
};

/**
 *  Draws the markers and boundaries
 */
function igdraw_markers(){
  // Draw boundaries
  draw_boundaries(boundaries);

  // Draw center markers
  if((show == 'cen' || show == 'all')){
    igdraw_cenmarkers(cenmarkers);
  }

  // Draw individual markers
  if((show == 'ind' || show == 'all')){
    igdraw_indmarkers(indmarkers);
  }
  // Pan to center if no markers
  if(markers.length == 0){
    map.panTo(center);
  }
  else{
    map.fitBounds(markerBounds);
  }
};

/**
 *  Draws individual markers for the park
 */
function igdraw_indmarkers(inds){

  var marker_i = [];
  for(i = 0; i < inds.length; i++){
    var Position = new google.maps.LatLng(inds[i].location.latitude,
                                          inds[i].location.longitude);
    marker_i[i] = new google.maps.Marker({
      position: Position,
      map: map,
      icon: inds[i].marker
    });
    markers.push(marker_i[i]);
    markerBounds.extend(Position);

  // Infobox html
    // Image
    var html = "<img src=" + inds[i].images.thumbnail + "><br><br>";
    html += "<span class='text-muted'>";
    // Cluster name
    html += "<span class='markertext'>Cluster:</span> " +
            inds[i].cluster + "<br>";
    // Latitude and Longitude
    html += "<span class='markertext'>Latitude:</span> " +
            inds[i].location.latitude.toFixed(2) + " <br>";
    html += "<span class='markertext'>Longitude:</span> " +
            inds[i].location.longitude.toFixed(2) + " <br>";
    // In park
    //html += "<span class='markertext'>Core Point:</span> " +
    //        inds[i].core + " <br>";
    html += "</span>";

    google.maps.event.addListener(marker_i[i], 'click',
      getInfoCallback(map, html));
  }
};

/**
 *  Draws cluster center markers for park
 */
function igdraw_cenmarkers(cens){

  var marker_c = [];

  for(i = 0; i < cens.length; i++){
    var Position = new google.maps.LatLng(cens[i].latitude,
                                          cens[i].longitude);
    marker_c[i] = new google.maps.Marker({
      position: Position,
      map: map,
      icon: cens[i].marker,
    });
    markers.push(marker_c[i]);
    markerBounds.extend(Position);

    // Infobox html
      var html = "<span class='text-muted'>";
      // Cluster name
      html += "<span class='markerhead'>Scene " +
              cens[i].cluster + "</span><br><br>";
      // Latitude and Longitude
      html += "<span class='markertext'>Latitude:</span> " +
              cens[i].latitude.toFixed(2) + " <br>";
      html += "<span class='markertext'>Longitude:</span> " +
              cens[i].longitude.toFixed(2) + " <br>";
      // Number of photos and users
      html += "<span class='markertext'># Photos:</span> " +
              cens[i].nophotos + " <br>";
      //html += "<span class='markertext'># Users:</span> " +
      //        cens[i].nousers + " <br>";
      html += "</span>"

      google.maps.event.addListener(marker_c[i], 'click',
        getInfoCallback(map, html));


  }
};
