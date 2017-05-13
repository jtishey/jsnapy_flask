$(document).ready(function(){
// Hide port divs for LAG
    $('.pass-child').hide();
    $('.fail-child').hide();
    $('.skip-child').hide();
});

$('#output_div').on('click', '.pass-main', function(){
    // Click output div to toggle child div
     $('.pass-child', this).toggle(); // p00f
});

$('#output_div').on('click', '.fail-main', function(){
    // Click output div to toggle child div
     $('.fail-child', this).toggle(); // p00f
});

$('#output_div').on('click', '.skip-main', function(){
    // Click output div to toggle child div
     $('.skip-child', this).toggle(); // p00f
});
