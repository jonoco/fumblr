import axios from 'axios';
import PostModal from './post-modal';
import { askConfirm } from './confirm-modal';

(function() {
    // Check browser compatibility for form support
    const isAdvancedUpload = function() {
      const div = document.createElement('div');
      return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) 
        && 'FormData' in window && 'FileReader' in window;
    }();

    function checkAdvancedUpload() {
        if (!isAdvancedUpload) {
            alert(`advanced upload not supported: 
                FormData| ${'FormData' in window}
                FileReader| ${'FileReader' in window}`);
        } else {
            alert(`supporting advanced upload: 
                FormData| ${'FormData' in window}
                FileReader| ${'FileReader' in window}`);
        }
    }

    const postModal = new PostModal();
    postModal.init();

    // View messages
    $('.message-user').on('click', openUserMessages);
    function openUserMessages(e) {
        const user = $(this).addClass('selected').data('user');
        $(`.message-user[data-user!='${user}']`).removeClass('selected');
        $(`.user-messages[data-user!='${user}']`).addClass('hide');
        const msgList = $(`.user-messages[data-user='${user}']`).removeClass('hide');
    }
    
    // Comment modal
    $('.comment-btn').on('click', openCommentModal);
    function openCommentModal() {
        const post = $(this).data('post');

        const $cmtModal = $('#comment-modal');
              $cmtModal.find('.comment-form').data('post', post);
              $cmtModal.find('.comment-text').val('');

        $cmtModal.modal('show');
    }

    $('.comment-form').on('submit', sendComment);
    function sendComment(e) {
        e.preventDefault();
        
        const $cmtModal = $('#comment-modal');
        const $form = $cmtModal.find('.comment-form');
        const post = $form.data('post');
        const text = $form.find('.comment-text').val();

        axios.post('/comment', {
            post, 
            text
        }).then(res => {
            if (res.data.comment) {
                $cmtModal.modal('hide');    
            } else {
                document.location.assign(res.request.responseURL);
            }
        }).catch(err => {
            console.log(err);
        });
    }

    // Message modal
    $('.msg-btn').on('click', openMsgModal);
    function openMsgModal() {
        const user = $(this).data('user');

        const $msgModal = $('#message-modal');
              $msgModal.find('.message-form').data('user', user);
              $msgModal.find('.message-text').val('');

        $msgModal.modal('show');
    }

    // Send message
    $('.message-form').on('submit', sendMessage);
    function sendMessage(e) {
        e.preventDefault();
        
        const $msgModal = $('#message-modal');
        const $form = $msgModal.find('.message-form');
        const user = $form.data('user');
        const text = $form.find('.message-text').val();

        axios.post('/message', {
            user, 
            text
        }).then(res => {
            console.log(res);
            $msgModal.modal('hide');

        }).catch(err => {
            console.log(err);
        });
    }

    // Delete button
    const $deleteBtn = $('.delete-btn');
    if (!!$deleteBtn) {
        $deleteBtn.on('click', (e) => {
            const btn = e.currentTarget;
            const postID = btn.dataset.post;

            askConfirm({ title: 'Delete post?', btn: 'Delete' })
            .then(() => {
                axios.get(`/post/delete/${postID}`)
                .then(res => {
                    document.location.reload(true);
                })
                .catch(err => {
                    console.log(err);
                });
            }).catch(() => {
                console.log('delete cancelled');
            });
        });
    }

    // Follow button
    $('.follow-btn').on('click', followUser);
    function followUser(e) {
        const $btn = $(this);
        const user = $btn.data('user');

        axios.post('/follow', {
            user
        }).then(res => {
            if (res.data.follow) {
                $btn.toggleClass('following');    
            } else {
                document.location.assign(res.request.responseURL);
            }
            
        }).catch(err => {
            console.log(err);
        });
    }

    // Like buttons
    const likeButtons = document.querySelectorAll('.like-btn');
    if (!!likeButtons) {
        likeButtons.forEach( btn => {
            btn.addEventListener('click', likePost);
        });
    }

    function likePost(e) {
        const btn = e.currentTarget;
        const postID = btn.dataset.post;

        axios.post('/like', {
            post: postID
        }).then(res => {
            if (res.data.like) {
                btn.classList.toggle('liked');    
            } else {
                document.location.assign(res.request.responseURL);
            }
        }).catch(err => {
            console.log(err.response);
        });
    }

    // Reblog button
    $('.reblog-btn').on('click', reblogPost);
    function reblogPost(e) {
        const postID = $(this).data('post');

        axios.get(`/reblog/${postID}`)
        .then(res => {
            if (res.data.post) {
                const post = JSON.parse(res.data.post);
                openReblogModal(post);    
            } else {
                document.location.assign(res.request.responseURL);
            }   
        })
        .catch(err => {
            console.log(err);
        });
    }

    function openReblogModal(post) {
        const $reblogModal = $('#reblog-modal');
              $reblogModal.find('.reblog-form').attr('action', `/reblog/${post.id}`);
              $reblogModal.find('.text').val('');
              $reblogModal.find('.tags').val('');
        const $preview = $reblogModal.find('.preview');
              $preview.empty();

        post.images.forEach(image => {
            $('<img class="image" />').attr('src', image.link).appendTo($preview);
        });
        $reblogModal.modal('show');
    }

    // Mobile header-sidebar
    $('.menu-btn, .mask').on('click', openSidemenu);
    function openSidemenu(e) {
        $('#header-sidebar').toggleClass('open');
        $('.menu-btn').toggleClass('fa-bars').toggleClass('fa-close');
    }

}());