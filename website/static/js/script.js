$(function() {
    $('#description-btn').click(function(){
        $('#description-top').hide();
        $('#description-bot').show();
    });

    $('#description-cancel').click(function(){
        $('#description-top').show();
        $('#description-bot').hide();
    })
});

