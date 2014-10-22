$(window).scroll(sidebarAffix);
$(window).resize(sidebarAffix);
function sidebarAffix() {
    if ($(window).width() > 992) {
        $('.navbar').affix({
            offset: {
                top: 0
            }
        });
    }
    else {
        $(window).off('.affix');
        $('.navbar').removeData('bs.affix').removeClass('affix affix-top affix-bottom')
    }
}

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
