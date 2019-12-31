$(document).ready(function(){

//     $('#add_review').on('click', function(){
//         var course_id = $(this).attr('course_id');

//         req = $.ajax({
//             url: '/add_review',
//             type: 'POST',
//             data: {id: course_id}
//         });

//         req.done(function(data) {

//         });
//     });


$('.port-item').click(function () {
    $('.collapse').collapse('hide');
  });

  $(document).on('click', '[data-toggle="lightbox"]', function (e) {
    e.preventDefault();
    $(this).ekkoLightbox();
  });






});
