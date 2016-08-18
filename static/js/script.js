$(function() {
    var timerId = null;
    var saveMemo = function() {
        var text = $('#memo').val();
        
        if (timerId !== null) {
            clearTimeout(timerId);
            timerId = null;
            $(window).off('beforeunload');
        }
        timerId = setTimeout(function() {
            $.post('/private/api/update',
                {'text': encodeURIComponent(text), 'url': current_url, 'api': api_id},
                function(data, textStatus, jqXHR) {
                    timerId = null;
                    $(window).off('beforeunload');
                }
            );
        }, 1000);
        $(window).on('beforeunload', function() {
            return 'まだ入力内容が保存されていません。\n数秒お待ちください。';
        });
    }
    
    $('#memo').keyup(function() {
        saveMemo();
    });
    $('#memo').mousedown(function() {
        saveMemo();
    });
    
    $('.popover-markup>.trigger').popover({
        html: true,
        title: function () {
            return $(this).parent().find('.head').html();
        },
        content: function () {
            return $(this).parent().find('.content').html();
        }
    });
    
    $(document).on('click','#submit-url-button',function() {
        var url = $('#input-url').val();
        if (url === current_url) {
            return false;
        }
        $.post('/private/api/change',
            {'url': url},
            function(data, textStatus, jqXHR) {
                if (data === "True") {
                    $('#change-url').submit();
                } else {
                    alert('そのURLは使用できません。');
                }
            }
        );
        return false;
    });
    
    $(document).on('click','#submit-password-button',function() {
        var password = $('#input-password').val();
        if (password.match(/^[\x20-\x7E]+$/)) {
            return true
        }
        alert('パスワードに使用できない文字が含まれています。');
        return false;
    });
    
    $('#change-public').change(function() {
        $.post('/private/api/public',
            {'url': current_url, 'flag': $(this).is(':checked'), 'api': api_id},
            function(data, textStatus, jqXHR) {

            }
        );
    });
});