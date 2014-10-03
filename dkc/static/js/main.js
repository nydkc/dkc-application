$(window).scroll(function() {
    if ($(window).width() > 992) {
        $('.sidebar').affix({
            offset: {
                top: 0
            }
        });
    }
});

$(function() {
    //$('a[href*=#]:not([href=#])').click(function() {
    $('.home a[href*=#]:not([href=#])').click(function() {
        if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
            if (target.length) {
                $('html,body').animate({
                    scrollTop: target.offset().top
                }, 1000);
                return false;
            }
        }
    });
});

$('.panel-collapse').each(function() {
    $(this).on('shown.bs.collapse', function() {
        $('html, body').animate({
            scrollTop: $(this).parent().offset().top
        }, 1000);
    });
});
