'use strict';

(function () {

    // Search bar
    var searchBar = document.querySelector('#search-bar');
    searchBar.addEventListener('submit', search);

    function search(e) {
        console.log(e);
    }

    // Like buttons
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
            btn.classList.toggle('liked');
        }).catch(function (err) {
            console.log(err);
        });
    }
})(axios);