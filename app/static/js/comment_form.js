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
            var comment = '';
            if (data.message.type === 'success') {
                bootstrap_alert = '<div class="alert alert-success">' +
                    '<button type="button" class="close" data-dismiss="alert">&times;</button>'+
                    data.message.body+
                    '</div>';
                comment = '<div class="media"><a href="#" class="pull-left" >' +
                    '<img src="'+ data.comment.avatar_hash + '" class="pull-left" alt="avatar">' +
                    '</a>' +
                    '<div class="media-body"><h4 class="media-body">' +
                    data.comment.author_email + '<small> ' + moment(data.comment.timestamp).fromNow() + '</small>' +
                    '</h4>' +
                    data.comment.body +
                    '</div></div>';
                $('.media:first').prepend(comment).hide().fadeIn('slow');
                $('#email').val('');
                $('#body').val('');
            }
            else
                bootstrap_alert = '<div class="alert alert-danger">' +
                    '<button type="button" class="close" data-dismiss="alert">&times;</button>'+
                    data.message.body+
                    '</div>';
            $('.well.well-form').prepend(bootstrap_alert).hide().fadeIn('slow');
        });
        event.preventDefault();
    })
});