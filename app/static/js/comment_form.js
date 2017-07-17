$(document).ready(function () {
    $('form').on('submit', function (event) {
        $.ajax({
            data: {
                'email': $('#email').val(),
                'body': $('#body').val(),
                'csrf_token': $('#csrf_token').val()
            },
            type: 'POST',
            url: $('form').attr('action')
        }).done(function (data) {
            var bootstrap_alert = '';
            if (data.message.type === 'success') {
                bootstrap_alert = '<div class="alert alert-success">' +
                    '<button type="button" class="close" data-dismiss="alert">&times;</button>'+
                    data.message.body+
                    '</div>';
            }
            else
                bootstrap_alert = '<div class="alert alert-danger">' +
                    '<button type="button" class="close" data-dismiss="alert">&times;</button>'+
                    data.message.body+
                    '</div>';
            $('.well.well-form').prepend(bootstrap_alert);
        });
        event.preventDefault();
    })
});