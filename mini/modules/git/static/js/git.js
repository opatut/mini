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

});
