$(document).ready(function() {

	// $('#review_form').on('submit', function(event) {
    //     var course_id = $(this).attr('course_id');
	// 	$.ajax({
	// 		data : {
    //             course_id: course_id,
	// 			rate : $("#review_form #rate").val(),
	// 			content : $('#review_form #content').val()
	// 		},
	// 		type : 'POST',
	// 		url : '/review_form'
	// 	})
	// 	.done(function(data) {
    //         $('#addRate').modal('toggle');
	// 		if (data.error) {
	// 			$('#errorAlert').text(data.error).show().delay(2500).fadeOut();
	// 			$('#successAlert').hide();
	// 		}
	// 		else {
	// 			$('#successAlert').text("your rate has been added succefully.").show().delay(2500).fadeOut();
    //             $('#errorAlert').hide();
                
	// 			$('#add-rate-link').text("Edit Rate");
				
	// 		}

	// 	});

	// 	event.preventDefault();

    // });
    

    $('#list_form').on('submit', function(event) {
        // input[value='Hot Fuzz']
        var course_id = $(this).attr('course_id');
		$.ajax({
			data : {
                course_id: course_id,
				status : $("#list_form #status").val(),
			},
			type : 'POST',
			url : '/list_form'
		})
		.done(function(data) {
            $('#addToList').modal('toggle');
			// if (data.error) {
			// 	$('#errorAlert').text(data.error).show();
			// 	$('#successAlert').hide();
			// }
			// else {
				$('#successAlert').text("The course has been added as " + data.status).show().delay(2500).fadeOut();
                $('#errorAlert').hide();

                $('#add-list-link').text("Added to " + data.status + " list");
                
			// }

		});

		event.preventDefault();

    });
    

// ------------------------------

    $('#delete_list').on('click', function(event) {
        var course_id = $(this).attr('course_id');
		$.ajax({
			data : {
                course_id: course_id
			},
			type : 'POST',
			url : '/delete_list'
		})
		.done(function(data) {
            $('#addToList').modal('toggle');
            $("#list_form #status").val("");
			if (data.error) {
				$('#errorAlert').text(data.error).show().delay(2500).fadeOut();
				$('#successAlert').hide();
			}
			else {
				$('#successAlert').text(data.done).show().delay(2500).fadeOut();
                $('#errorAlert').hide();

                $('#add-list-link').text("Add to list");
                
			}

		});

		event.preventDefault();

    });
    

    // $('#delete_review').on('click', function(event) {
    //     var course_id = $(this).attr('course_id');
	// 	$.ajax({
	// 		data : {
    //             course_id: course_id,
	// 		},
	// 		type : 'POST',
	// 		url : '/delete_review'
	// 	})
	// 	.done(function(data) {
    //         $('#addRate').modal('toggle');
    //         $("#review_form #rate").val("");
	// 		$("#review_form #content").val("");
			
	// 		// window.location.reload();
			
	// 		if (data.error) {
	// 			$('#errorAlert').text(data.error).show().delay(2500).fadeOut();
    //             $('#successAlert').hide();
	// 		}
	// 		else {
	// 			$('#successAlert').text(data.done).show().delay(2500).fadeOut();
    //             $('#errorAlert').hide();

    //             $('#add-rate-link').text("Rate and Review");
                
	// 		}

	// 	});

	// 	event.preventDefault();

	// });

});




