$(document).ready(function() {
    $('#platform').change(function() {
        if ($(this).val() === 'youtube') {
            $('#quality-group').slideDown();
        } else {
            $('#quality-group').slideUp();
        }
    });

    $('#download-form').submit(function(e) {
        e.preventDefault();

        const url = $('#url').val();
        const platform = $('#platform').val();
        const quality = $('#quality').val();

        if (!url || !platform) {
            showMessage('Please provide all required fields.', 'danger');
            return;
        }

        $('.progress').show();
        $('.progress-bar').css('width', '25%').text('Starting...');

        $.ajax({
            url: '/download',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ url, platform, quality }),
            success: function(response) {
                $('.progress-bar').css('width', '100%').text('Completed');
                showMessage(response.message, 'success');
                $('.progress').delay(2000).slideUp();
                const downloadLink = `<a href="/download_file/${response.filename}" class="btn btn-success mt-3">Download File</a>`;
                $('#message').append(downloadLink);
            },
            error: function(xhr) {
                $('.progress').hide();
                showMessage(xhr.responseJSON.message || 'An error occurred.', 'danger');
            }
        });
    });

    function showMessage(message, type) {
        const alertDiv = `<div class="alert alert-${type}" role="alert">${message}</div>`;
        $('#message').html(alertDiv);
    }
});
