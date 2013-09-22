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
    })
});
