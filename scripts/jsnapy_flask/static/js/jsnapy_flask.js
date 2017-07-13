$(document).ready(function(){
    // Hide port divs for LAG
    $('.pass-child').hide();
    $('.fail-child').hide();
    $('.skip-child').hide();

    // Hide settings section
    $('#settings-div').hide()

// Toggle button for Pre vs Post
$('.btn-toggle').click(function() {
    $(this).find('.btn').toggleClass('active');  

    if ($(this).find('.btn-primary').size()>0) {
        $(this).find('.btn').toggleClass('btn-primary');
    }
    if ($(this).find('.btn-danger').size()>0) {
        $(this).find('.btn').toggleClass('btn-danger');
    }
    if ($(this).find('.btn-success').size()>0) {
        $(this).find('.btn').toggleClass('btn-success');
    }
    if ($(this).find('.btn-info').size()>0) {
        $(this).find('.btn').toggleClass('btn-info');
    }

    $(this).find('.btn').toggleClass('btn-default');
    if ($('#pre_toggle').hasClass("active")) {
        $('#snap').val('pre');
    } else {
        $('#snap').val('post')
    }
    return false;
});

// Show settings section on icon click
$('#settings').click(function () {
    $('#settings-div').toggle(500)
});

// Submit settings form when Update button is clicked
$('#settings_update').click(function() {
     $('#settings-div').hide(500)
    $.ajax({
        url: "./jsnapy_settings",
        data: $('form').serialize(),
        type: 'POST',
        timeout: 3000,
    });
});

// Submit the snapshot form on button click
$('#submit_form').click(function () {
    $.LoadingOverlay("show");
    $.ajax({
        url: "./jsnapy_flask",
        data: $('form').serialize(),
        type: 'POST',
        error: function(){ $.LoadingOverlay("hide"); },
        timeout: 30000,
        success: function(response) {
            $.LoadingOverlay("hide");
            if (response.error != "") {
                $('#output_div').html(response.error)
            } else {
                $('#output_div').html(response.data)
            }
        }
    });
});

});