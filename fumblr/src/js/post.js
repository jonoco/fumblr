import axios from 'axios';
import { askConfirm } from './confirm-modal';

// Delete button
const $deleteBtn = $('.post .delete-btn');
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