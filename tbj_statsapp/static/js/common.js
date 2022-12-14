// Highlight active page
$(function () {
  $("a").each(function () {
    if ($(this).prop("href") == window.location.href) {
      $(this).addClass("active");
      $(this).parents("li").addClass("active");
    }
  });
});

// Show default views on page load
$(function () {
  $(".toHide").hide()
  $("#Hitters").show();
});

// Toggle divs
$(function () {
  $("input[type=radio]").click(function () {
    $(".toHide").hide();
    $("#" + $(this).val()).show();
  });
});
