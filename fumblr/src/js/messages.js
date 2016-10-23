import axios from 'axios';

export default class Messages {
    constructor() {
        this.$messages = $('#messages');
        this.$form = this.$messages.find('form');
        this.$messageBar = this.$messages.find('.message-bar');
        this.$messageUser = $('.message-user');

        this.$messageUser.on('click', this.openUserMessages.bind(this));
        this.$form.on('submit', this.sendMessage.bind(this));

        // Message modal
        $('.msg-btn').on('click', this.openMsgModal); 
    }

    sendMessage(e) {
        e.preventDefault();
        
        const $form = $('#messages form');
        const url = $form.attr('action');
        const text = $form.find('.message-text').val();
        $form.find('.message-text').val('');

        axios.post(url, {
            text
        }).then(res => {
            console.log(res.data);
            this.addMessage(res.data.message, res.data.user);
        }).catch(err => {
            console.log(err);
        });
    }

    openUserMessages(e) {
        const user = $(e.currentTarget).addClass('selected').data('user');
        this.$messages.find(`.message-user[data-user!='${user}']`).removeClass('selected');
        this.$messages.find(`.user-messages[data-user!='${user}']`).addClass('hide');
        this.$messages.find(`.user-messages[data-user='${user}']`).removeClass('hide');
        
        this.$messageBar.removeClass('hide');
        this.$messages.find('form').attr('action', `/message/user/${user}`);       

        const messageList = this.$messages.find(`.user-messages[data-user='${user}']`);
        const height = messageList.height();
        messageList.scrollTop(height);
    }

    addMessage(msg, user) {
        const $newMsg = $(msg);
        const $messageList = this.$messages.find(`.user-messages[data-user='${user}']`);
        $messageList.append($newMsg);
        $messageList.scrollTop($messageList.height());
    }

    openMsgModal() {
        const user = $(this).data('user');

        const $msgModal = $('#message-modal');
              $msgModal.find('.message-text').val('');
        const $form = $msgModal.find('form');
              $form.attr('action', `/message/user/${user}`); 
              $form.on('submit', () => { $msgModal.modal('hide'); })      

        $msgModal.modal('show');
    }
}