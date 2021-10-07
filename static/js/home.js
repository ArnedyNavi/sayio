$(function() {
  $("#unfollowing").click(function() {
    var user = $(this).attr('name');
    var dataString = 'user='+ user;
    //alert (dataString);return false;

    $.ajax({
      type: "POST",
      url: "/follow",
      data: dataString,
      success: function() {
        $("#unfollowing").removeClass("unfollowing-user").addClass("following-user");
        $("#unfollowing").attr('id', "following");
        $("#following").html('<span class="following-text">Following</span><span id="unfollow-text" class="unfollow-text">Unfollow</span>');
      }
    });
    return false;
    });
  $("#following").click(function() {
    var user = $(this).attr('name');
    var dataString = 'user='+ user;


    $.ajax({
      type: "POST",
      url: "/unfollow",
      data: dataString,
      success: function() {
        $("#following").removeClass("following-user").addClass("unfollowing-user");
        $("#following").attr('id', "unfollowing");
        $("#unfollowing").html('<span class="follow-text">Follow</span>');
      }
    });
    return false;
    });

  $("i[name^='like-btn']").click(function() {
    var post_id = $(this).attr('id');
    var dataString = 'post=' + post_id;

    $.ajax({
      type: "POST",
      url: "/like",
      data: dataString,
      success: function() {
        $('#' + post_id).removeClass("fa-outline").addClass("fa-fill-2")
      }
    });
    return false;
    });
  $("i[name^='dislike-btn']").click(function() {
    var post_id = $(this).attr('id');
    var dataString = 'post=' + post_id;

    $.ajax({
      type: "POST",
      url: "/dislike",
      data: dataString,
      success: function() {
        $('#' + post_id).removeClass("fa-fill-2").addClass("fa-outline")
      }
    });
    return false;
    });
});


let btn = document.getElementById("btn-post");
let modal = document.querySelector(".modal");
let closeBtn = document.querySelector(".closebtn");


btn.onclick = function(){
  modal.style.display = "block";
}

closeBtn.onclick = function(){
  modal.style.display = "none";
}

window.onclick = function(e){
  if(e.target == modal){
    modal.style.display = "none";
  }
}

let input = document.getElementById("content")

if (input.length > 100) {
  window.alert("More than 100")
}



