Suit.$(document).ready(function () {
    Suit.$(".field-image").
    each(function () {
        var tag_a = Suit.$(this).children('a');
        var img = "<img src=%url style='width: 150px; height: 60px;'>".replace('%url', tag_a.attr('href'));
        tag_a.html(img)
    })
});
