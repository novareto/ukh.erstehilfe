$(document).ready(function() {
    $("#remote-form form").submit(function(event) {
	event.preventDefault();
	var basic = $("#remote-form").attr("rel");
	var formData = new FormData($(this)[0]);
    formData.append('form.action.calculate', 'Berechnen und eintragen')
	$.ajax({
            url: $(this).attr('action'),
            type: 'post',
            data: formData,
	    cache: false,
	    contentType: false,
	    processData: false,
	    headers: {
		"Authorization": "Basic " + basic
	    },
            success: function(data) {
                console.log('ALLES GUT')
                console.log(data)
                if (data.search('Fehler') > 0 ) {
                    $('form').html($(data).find('form').html())
                }
                else {
		            location.reload();
                }
            },
            error: function(xhr, error) {
                console.log('ERROR')
                location.reload()
            }
	});
    });
})
