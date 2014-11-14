$(document).ready(function() {
    $('body').scrollspy({
        target: '.application-sections',
        offset: 40
    });
    $('.tooltip-trigger').each(function() {
        $(this).tooltip({});
    });
});
