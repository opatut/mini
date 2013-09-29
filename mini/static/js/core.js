$(document).ready(function() {
    $(".issue-status-select").change(function() {
        $(this)
            .removeClass("closed")
            .removeClass("open")
            .removeClass("wip")
            .removeClass("discussion")
            .removeClass("invalid")
            .addClass($(this).val());
    });

    $(".issue-tag-select input").change(function() {
        if($(this)[0].checked) {
            $(this).parents("li").removeClass("inactive").addClass("active");
        } else {
            $(this).parents("li").removeClass("active").addClass("inactive");
        }
    });

    $(".color-picker li span").click(function() {
        $($(this).parents(".color-picker").attr("data-input")).val($(this).attr("data-color"));
    });

    $(".color-picker").each(function() {
        var cp = $(this);
        var input = $(cp.attr("data-input"));

        function update_color() {
            var v = $(this).val();
            input.parent().find(".color-display").css("background-color", "#" + (v.length%3==0 ? v||"FFF" : "FFF"));
        }

        $(this).find("li span").click(function() {
            input.val($(this).attr("data-color"));
            update_color.call(input);
        });

        input.keyup(update_color);
        update_color.call(input);
    });

    $(".color-picker-input").change(function() {
    });

    $(".tag-edit-list tr").click(function() {
        window.location.href = $(this).find(".edit-link").attr("href");
    }).css("cursor", "pointer");
});
