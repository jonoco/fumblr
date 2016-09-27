'use strict';

(function () {

    var isAdvancedUpload = function () {
        var div = document.createElement('div');
        return ('draggable' in div || 'ondragstart' in div && 'ondrop' in div) && 'FormData' in window && 'FileReader' in window;
    }();

    // Post Button
    $('.post-btn').on('click', openUploadModal);

    // Edit Button
    $('.edit-btn').on('click', editPost);

    function editPost() {
        var postID = $(this).data('post');

        axios.get('/post/edit/' + postID).then(function (res) {
            var post = JSON.parse(res.data.post);
            openEditModal(post);
        }).catch(function (err) {
            console.log(err);
        });
    }

    // Open post modal for uploading
    function openUploadModal() {
        var postModal = $('#post-modal');
        postModal.find('.post-form').attr('action', '/post');

        var preview = postModal.find('.preview');
        preview.empty();

        openPostModal();
    }

    // Open post modal for editing
    function openEditModal(post) {
        var postModal = $('#post-modal');
        postModal.find('.modal-title').text('Edit Post');
        postModal.find('.submit-btn').text('Save Changes');
        postModal.find('.text').val(post.text);
        postModal.find('.tags').val(post.tags.join(', '));
        postModal.find('.post-form').attr('action', '/post/edit/' + post.id);

        var preview = postModal.find('.preview');
        preview.empty();

        var img = $('<img class="image" />');
        img.attr('src', post.link);
        img.appendTo(preview);

        openPostModal();
    }

    // Post modal
    function openPostModal() {
        var postModal = $('#post-modal');

        var form = postModal.find('.post-form');
        var text = postModal.find('.text');
        var tags = postModal.find('.tags');
        var preview = postModal.find('.preview');
        var file = postModal.find('.photo');
        file.change(function (e) {
            handleFiles(e.currentTarget.files);
        });
        var submitBtn = postModal.find('.submit-btn');
        submitBtn.on('click', submit);

        var droparea = postModal.find('.droparea');
        var dropbox = postModal.find('.dropbox');
        dropbox.on('dragenter', dragenter);
        dropbox.on('dragover', dragover);
        dropbox.on('dragleave', dragleave);
        dropbox.on('drop', drop);

        var formData = new FormData();

        postModal.modal('show');

        function addPreviewImage(files) {
            preview.empty();
            var img = $('<img class="image" />');

            var reader = new FileReader();
            reader.onload = function (aImg) {
                return function (e) {
                    aImg.attr('src', e.target.result);
                };
            }(img);
            reader.readAsDataURL(files[0]);

            img.appendTo(preview);
        }

        function handleFiles(files) {
            addPreviewImage(files);

            $.each(files, function (i, file) {
                formData.set('file', file);
            });
        }

        function submit() {
            if (form.hasClass('is-uploading')) return false;

            form.addClass('is-uploading');
            formData.set('text', text.val());
            formData.set('tags', tags.val());

            var url = postModal.find('.post-form').attr('action');

            axios.post(url, formData).then(function (res) {
                form.removeClass('is-uploading');
                window.location.replace(res.request.responseURL);
            }).catch(function (err) {
                console.log(err);
            });
        }

        function drop(e) {
            e.stopPropagation();
            e.preventDefault();

            var files = e.originalEvent.dataTransfer.files;
            handleFiles(files);
        }

        function dragenter(e) {
            e.stopPropagation();
            e.preventDefault();
            droparea.addClass('dragover');
        }

        function dragleave(e) {
            e.stopPropagation();
            e.preventDefault();
            droparea.removeClass('dragover');
        }

        function dragover(e) {
            e.stopPropagation();
            e.preventDefault();
        }
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