var MIN_LENGTH = 1;
var current = -1;

$( document ).ready(function() {

	$("#keyword").keyup(function(e) {

		var $hlight = $('div.item');
		var names = [];
		$hlight.each(function() { names.push($(this).text()) });

		// Key down
		if (e.keyCode == 40) {
			$('div.hlight').toggleClass("hlight");
				current = current + 1;
				if (current == $hlight.length){
					current = 0;
				}
				$("#keyword").val(names[current]);
				$hlight.eq(current).toggleClass( "hlight" );
		}
		// Key up
		else if (e.keyCode == 38) {
				// Turn off highlighting
				$('div.hlight').toggleClass("hlight");
				current = current - 1;
				if (current < 0){
					current = $hlight.length-1;
				}
				$("#keyword").val(names[current]);
				$hlight.eq(current).toggleClass( "hlight" );
		}
		else {
					current = -1;
					var keyword = $("#keyword").val();
					if (keyword.length >= MIN_LENGTH) {
						$.get( "autocomplete", { keyword: keyword } )

						.done(function( data ) {

							$('#results').html('');
							var results = data["data"];

							$.each(results, function(key, value) {
								$('#results').append('<div class="item">' + value + '</div>');
							})



						    $('.item').click(function() {
						    	var text = $(this).html();
						    	$('#keyword').val(text);
									$('#parksearch').submit();
						    })

						});
					} else {
						$('#results').html('');
					}
		}
	});

    $("#keyword").blur(function(){
    		$("#results").fadeOut(500);
    	})
        .focus(function() {
    	    $("#results").show();
    	});


});
