// Highlight active page
$(function () {
  $("a").each(function () {
    if ($(this).prop("href") == window.location.href) {
      $(this).addClass("active");
      $(this).parents("li").addClass("active");
    }
  });
});

// Hide pitcher div on load
$(function () {
  $("#Hitters").show();
  $("#Pitchers").hide();
});

// Toggle hitter / pitcher divs
$(function () {
  $("input[name=playerType]").click(function () {
    $("#Hitters").hide();
    $("#Pitchers").hide();
    $("#" + $(this).val()).show();
  });
});
