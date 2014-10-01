$(window).scroll(function() {
    if ($(window).width() > 992) {
        $('.sidebar').affix({
            offset: {
                top: 0
            }
        });
    }
});
