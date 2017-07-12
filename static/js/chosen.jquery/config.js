Suit.$(document).ready(function () {
    Suit.$("select[id^='id_group_buy_goods']").
    not('#id_group_buy_goods-__prefix__-goods').
    each(function () {
        Suit.$(this).chosen()
    })
});
