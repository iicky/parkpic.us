  var carousel = 0;
  var pind1 = 0;
  var pind2 = 1;
  var pind3 = 2;

  function preload(arrayOfImages) {
      $(arrayOfImages).each(function () {
          $('<img />').attr('src',this).appendTo('body').css('display','none');
      });
  }

  var primeCarousel = function(c){

    carousel = c;
    pind1 = 0;
    pind2 = 1;
    pind3 = 2;

    preload(cphotos[carousel]);

    $('#img1').attr('src', cphotos[carousel][pind1]);
    $('#img2').attr('src', cphotos[carousel][pind2]);
    $('#img3').attr('src', cphotos[carousel][pind3]);
    $('#exploremsg').hide();
    $('#topphotos').show();

  };


  $('#scrollright').click(function() {

      pind1 += 1;
      pind2 += 1;
      pind3 += 1;

      if(pind1 >= cphotos[carousel].length){ pind1 = 0; }
      if(pind2 >= cphotos[carousel].length){ pind2 = 0; }
      if(pind3 >= cphotos[carousel].length){ pind3 = 0; }

      $('#img1').attr('src', cphotos[carousel][pind1]);
      $('#img2').attr('src', cphotos[carousel][pind2]);
      $('#img3').attr('src', cphotos[carousel][pind3]);

  });

  $('#scrollleft').click(function() {

    pind1 -= 1;
    pind2 -= 1;
    pind3 -= 1;

    if(pind1 < 0){ pind1 = cphotos[carousel].length-1; }
    if(pind2 < 0){ pind2 = cphotos[carousel].length-1; }
    if(pind3 < 0){ pind3 = cphotos[carousel].length-1; }

    $('#img1').attr('src', cphotos[carousel][pind1]);
    $('#img2').attr('src', cphotos[carousel][pind2]);
    $('#img3').attr('src', cphotos[carousel][pind3]);});
