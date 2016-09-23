'use strict';

(function () {

    // Upload modal
    var uploadModal = document.querySelector('#upload-modal');
    if (uploadModal) {
        (function () {
            //TODO validate form behavior here
            var data = {};

            var form = uploadModal.querySelector('#upload-form');
            var droparea = uploadModal.querySelector('.droparea');
            var dropbox = uploadModal.querySelector('#dropbox');
            dropbox.addEventListener('dragenter', dragenter, false);
            dropbox.addEventListener('dragover', dragover, false);
            dropbox.addEventListener('dragleave', dragleave, false);
            dropbox.addEventListener('drop', drop, false);

            var uploadBtn = uploadModal.querySelector('#upload-btn');
            uploadBtn.addEventListener('click', upload);

            var file = uploadModal.querySelector('#photo');
            var text = uploadModal.querySelector('#text');
            var tags = uploadModal.querySelector('#tags');

            function upload(e) {
                data.text = text.value;
                data.tags = tags.value;
                data.file = file.files[0];

                form.submit();
            }

            function handleFiles(files) {
                file.files = files;
            }

            function drop(e) {
                e.stopPropagation();
                e.preventDefault();

                var dt = e.dataTransfer;
                var files = dt.files;

                handleFiles(files);
            }

            function dragenter(e) {
                e.stopPropagation();
                e.preventDefault();
                droparea.classList.add('dragover');
            }

            function dragleave(e) {
                e.stopPropagation();
                e.preventDefault();
                droparea.classList.remove('dragover');
            }

            function dragover(e) {
                e.stopPropagation();
                e.preventDefault();
            }
        })();
    }

    // Follow button
    var followButtons = document.querySelectorAll('.follow-btn');
    if (followButtons) {
        followButtons.forEach(function (btn) {
            btn.addEventListener('click', followUser);
        });
    }
    function followUser(e) {
        var btn = e.currentTarget;
        var user = btn.dataset.user;

        axios.post('/follow', {
            user: user
        }).then(function (res) {
            console.log(res.data.following);
            btn.classList.toggle('following');
        }).catch(function (err) {
            console.log(err);
        });
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