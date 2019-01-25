try{
    var sock = new WebSocket('ws://' + window.location.host + WS_URL);
}
catch(err){
    var sock = new WebSocket('wss://' + window.location.host + WS_URL);
}

var service_msg = '<div class="service-msg">{text}</div>', msg_template = `
<div class="media-body">
    <h5 class="mt-0 mb-1">@{username} <small>{time}</small></h5>
    {text}
</div>`, $chatArea = $('.current-chat-area'), $messagesContainer = $('#messages');

function dateFormat(date) {
    return [date.getFullYear(), ("0" + (date.getMonth() + 1)).slice(-2), ("0" + date.getDate()).slice(-2)].join('-') + ' ' +  [date.getHours(), date.getMinutes()].join(':');
}

function showMessage(message) {
    /* Append message to chat area */
    var data = jQuery.parseJSON(message.data);
    var date = new Date(data.time);   
    if (data.username) {
        var msg = msg_template
            .replace('{username}', data.username)
            .replace('{text}', data.text)
            .replace('{time}', dateFormat(date));

    } else {
        var msg = service_msg.replace('{text}', data.text.split('\n').join('<br />'));
    }
    $messagesContainer.append('<li class="media">' + msg + '</li>');
    $chatArea.scrollTop($messagesContainer.height());
}

$(document).ready(function(){
    $chatArea.scrollTop($messagesContainer.height());

    $('#send').on('submit', function (event) {
        event.preventDefault();
        var $message = $(event.target).find('input[name="text"]');
        if ($.trim($message.val()) === '') {
            console.log('Submited message is empty. Return!');
            $message.val('').focus();
            return false;
        }
        sock.send($message.val());
        $message.val('').focus();
    });

    sock.onopen = function (event) {
        console.log(event);
        console.log('Connection to server started');
    };

    sock.onclose = function (event) {
        console.log(event);
        if(event.wasClean){
            console.log('Clean connection end');
        } else {
            console.log('Connection broken');
        }
        window.location.assign('/');
    };

    sock.onerror = function (error) {
        console.log(error);
    };

    sock.onmessage = showMessage;
});
