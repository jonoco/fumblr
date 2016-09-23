'use strict';

(function () {

    // Upload modal
    var uploadModal = document.querySelector('#upload-modal');
    if (!!uploadModal) {
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

            var uploadBtn = uploadModal.querySelector('#submit-btn');
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

    // Edit modal
    var editModal = $('#edit-modal');
    if (!!editModal) {
        (function () {
            var file = editModal.find('#photo');
            var text = editModal.find('#text');
            var tags = editModal.find('#tags');
            var submitBtn = editModal.find('#submit-btn');
            submitBtn.on('click', submitEdit);

            var postID;

            $('.edit-btn').on('click', openPost);

            function openPost(e) {
                var btn = e.currentTarget;
                postID = btn.dataset.post;

                axios.get('/post/edit/' + postID).then(function (res) {
                    console.log(res);
                    editPost(JSON.parse(res.data.post));
                }).catch(function (err) {
                    console.log(err);
                });

                $(editModal).modal('show');
            }

            function editPost(post) {
                // update form fields from the post data received from server
                text.val(post.text);
                tags.val(post.tags.join(', '));
            }

            function submitEdit() {
                var post = {
                    id: postID,
                    text: text.val(),
                    tags: tags.val()
                };

                axios.post('/post/edit/' + postID, post).then(function (res) {
                    console.log(res);
                    document.location.reload(true);
                }).catch(function (err) {
                    console.log(err);
                });
            }
        })();
    }

    // Confirmation modal
    function askConfirm(_ref) {
        var _ref$text = _ref.text;
        var text = _ref$text === undefined ? 'Are you sure you want to do that?' : _ref$text;
        var _ref$title = _ref.title;
        var title = _ref$title === undefined ? 'Are you sure?' : _ref$title;
        var _ref$btn = _ref.btn;
        var btn = _ref$btn === undefined ? 'Confirm' : _ref$btn;

        return new Promise(function (resolve, reject) {
            var confirmModal = $('#confirm-modal');
            if (!!confirmModal) {
                confirmModal.find('.modal-title').text(title);
                confirmModal.find('#text').text(text);

                var submitBtn = confirmModal.find('#submit-btn');
                submitBtn.text(btn);
                submitBtn.on('click', resolve);

                var cancelBtn = confirmModal.find('#cancel-btn');
                cancelBtn.on('click', reject);

                confirmModal.modal({
                    backdrop: 'static',
                    keyboard: false
                });
            } else {
                reject('No confirm modal found');
            }
        });
    }

    // Delete button
    var deleteBtn = $('.delete-btn');
    if (!!deleteBtn) {
        deleteBtn.on('click', function (e) {
            var btn = e.currentTarget;
            var postID = btn.dataset.post;

            askConfirm({ title: 'Delete post?', btn: 'Delete' }).then(function () {
                axios.get('/post/delete/' + postID).then(function (res) {
                    console.log(res);
                    document.location.reload(true);
                }).catch(function (err) {
                    console.log(err);
                });
            }).catch(function () {
                console.log('delete cancelled');
            });
        });
    }

    // Follow button
    var followButtons = document.querySelectorAll('.follow-btn');
    if (!!followButtons) {
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
    if (!!likeButtons) {
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