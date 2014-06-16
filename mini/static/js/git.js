$(document).ready(function() {

    $("#branch-select").change(function() {
        window.location = $(this).val();
    });

    $(".image-preview .mode").click(function() {
        $(this).parent().find("button").removeClass("active");
        $(this).addClass("active");


        $(this).parents(".image-preview")
            .removeClass("transparent")
            .removeClass("black")
            .removeClass("white")
            .addClass($(this).attr("data-mode"));
    });

    $("#issue-status-footer").hide();
    var issue_status_original_data = $("#issue-status-form").serialize();

    $("#issue-status-form :input").on("change", function() {
        if ($("#issue-status-form").serialize() == issue_status_original_data) {
            $("#issue-status-footer").slideUp(100);
        } else {
            $("#issue-status-footer").slideDown(100);
        }
    });

    $(".branch-input").typeahead({source:branches, minLength: 0, showHintOnFocus: true}).attr("autocomplete", "off");
});
