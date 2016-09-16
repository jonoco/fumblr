'use strict';

(function () {

    var likeButton = document.querySelector('#like-btn');
    likeButton.addEventListener('click', function (e) {
        var postID = e.currentTarget.dataset.post;

        axios.post('/like', {
            post: postID
        }).then(function (res) {
            likeButton.classList.toggle('btn-success');
        }).catch(function (err) {
            console.log(err);
        });
    });
})(axios);