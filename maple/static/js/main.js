'use strict';

(function () {

    var likeButtons = document.querySelectorAll('.like-btn');
    if (likeButtons) {
        likeButtons.forEach(function (btn) {
            btn.addEventListener('click', likePost);
        });
    }

    function likePost(e) {
        var btn = e.currentTarget;
        var postID = btn.dataset.post;

        axios.post('/like', {
            post: postID
        }).then(function (res) {
            btn.classList.toggle('btn-success');
        }).catch(function (err) {
            console.log(err);
        });
    }
})(axios);