$(document).ready(function() {
    $('body').scrollspy({
        target: '.application-sections',
        offset: 20
    });
    $('.tooltip-trigger').each(function() {
        $(this).tooltip({});
    });
});
