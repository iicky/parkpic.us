$('<img />').attr('src','../static/images/contact_email.png').appendTo('body').css('display','none');
$('<img />').attr('src','../static/images/contact_resume.png').appendTo('body').css('display','none');
$('<img />').attr('src','../static/images/contact_linkedin.png').appendTo('body').css('display','none');
$('<img />').attr('src','../static/images/contact_github.png').appendTo('body').css('display','none');

$('#contactemail').hover(function(){
    $('#contactimg').attr('src', '../static/images/contact_email.png');
},function(){
    $('#contactimg').attr('src', '../static/images/contact_blank.png');
});

$('#contactresume').hover(function(){
    $('#contactimg').attr('src', '../static/images/contact_resume.png');
},function(){
    $('#contactimg').attr('src', '../static/images/contact_blank.png');
});

$('#contactlinkedin').hover(function(){
    $('#contactimg').attr('src', '../static/images/contact_linkedin.png');
},function(){
    $('#contactimg').attr('src', '../static/images/contact_blank.png');
});

$('#contactgithub').hover(function(){
    $('#contactimg').attr('src', '../static/images/contact_github.png');
},function(){
    $('#contactimg').attr('src', '../static/images/contact_blank.png');
});
