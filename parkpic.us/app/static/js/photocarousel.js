var carousel = 0;
var pind1 = 0;
var pind2 = 1;
var pind3 = 2;

function preload(arrayOfImages) {
    $(arrayOfImages).each(function () {
        $('<img />').attr('src',this['square_link']).appendTo('body').css('display','none');
    });
};

var primeCarousel = function(c){

    carousel = c;
    pind1 = 0;
    pind2 = 1;
    pind3 = 2;

    preload(cphotos[carousel]);
    $('#img1').attr('src', cphotos[carousel][pind1]['square_link']);
    $('#img2').attr('src', cphotos[carousel][pind2]['square_link']);
    $('#img3').attr('src', cphotos[carousel][pind3]['square_link']);

    $('#link1').attr('href',cphotos[carousel][pind1]['photopage']);
    $('#link2').attr('href',cphotos[carousel][pind2]['photopage']);
    $('#link3').attr('href',cphotos[carousel][pind3]['photopage']);

    $('#user1').text(cphotos[carousel][pind1]['username']);
    $('#user2').text(cphotos[carousel][pind2]['username']);
    $('#user3').text(cphotos[carousel][pind3]['username']);

    $('#date1').text(dateFormat(cphotos[carousel][pind1]['taken'], "mm/dd/yy hh:MM TT"));
    $('#date2').text(dateFormat(cphotos[carousel][pind2]['taken'], "mm/dd/yy hh:MM TT"));
    $('#date3').text(dateFormat(cphotos[carousel][pind3]['taken'], "mm/dd/yy hh:MM TT"));

    $('#exploremsg').hide();
    $('#topphotos').show();

  };

  // Scroll photos right
  $('#scrollright').click(function() {

    pind1 += 1;
    pind2 += 1;
    pind3 += 1;

    if(pind1 >= cphotos[carousel].length){ pind1 = 0; }
    if(pind2 >= cphotos[carousel].length){ pind2 = 0; }
    if(pind3 >= cphotos[carousel].length){ pind3 = 0; }

    $('#img1').attr('src', cphotos[carousel][pind1]['square_link']);
    $('#img2').attr('src', cphotos[carousel][pind2]['square_link']);
    $('#img3').attr('src', cphotos[carousel][pind3]['square_link']);

    $('#link1').attr('href',cphotos[carousel][pind1]['photopage']);
    $('#link2').attr('href',cphotos[carousel][pind2]['photopage']);
    $('#link3').attr('href',cphotos[carousel][pind3]['photopage']);

    $('#user1').text(cphotos[carousel][pind1]['username']);
    $('#user2').text(cphotos[carousel][pind2]['username']);
    $('#user3').text(cphotos[carousel][pind3]['username']);

    $('#date1').text(dateFormat(cphotos[carousel][pind1]['taken'], "mm/dd/yy hh:MM TT"));
    $('#date2').text(dateFormat(cphotos[carousel][pind2]['taken'], "mm/dd/yy hh:MM TT"));
    $('#date3').text(dateFormat(cphotos[carousel][pind3]['taken'], "mm/dd/yy hh:MM TT"));

  });

  // Scroll photos left
  $('#scrollleft').click(function() {

    pind1 -= 1;
    pind2 -= 1;
    pind3 -= 1;

    if(pind1 < 0){ pind1 = cphotos[carousel].length-1; }
    if(pind2 < 0){ pind2 = cphotos[carousel].length-1; }
    if(pind3 < 0){ pind3 = cphotos[carousel].length-1; }

    $('#img1').attr('src', cphotos[carousel][pind1]['square_link']);
    $('#img2').attr('src', cphotos[carousel][pind2]['square_link']);
    $('#img3').attr('src', cphotos[carousel][pind3]['square_link']);

    $('#link1').attr('href',cphotos[carousel][pind1]['photopage']);
    $('#link2').attr('href',cphotos[carousel][pind2]['photopage']);
    $('#link3').attr('href',cphotos[carousel][pind3]['photopage']);

    $('#user1').text(cphotos[carousel][pind1]['username']);
    $('#user2').text(cphotos[carousel][pind2]['username']);
    $('#user3').text(cphotos[carousel][pind3]['username']);

    $('#date1').text(dateFormat(cphotos[carousel][pind1]['taken'], "mm/dd/yy hh:MM TT"));
    $('#date2').text(dateFormat(cphotos[carousel][pind2]['taken'], "mm/dd/yy hh:MM TT"));
    $('#date3').text(dateFormat(cphotos[carousel][pind3]['taken'], "mm/dd/yy hh:MM TT"));

  });
