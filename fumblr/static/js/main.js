'use strict';

(function () {

    // View messages
    $('.message-user').on('click', openUserMessages);
    function openUserMessages(e) {
        var user = $(this).addClass('selected').data('user');
        $('.message-user[data-user!=\'' + user + '\']').removeClass('selected');
        $('.user-messages[data-user!=\'' + user + '\']').addClass('hide');
        var msgList = $('.user-messages[data-user=\'' + user + '\']').removeClass('hide');
    }

    // Check browser compatibility for form support
    var isAdvancedUpload = function () {
        var div = document.createElement('div');
        return ('draggable' in div || 'ondragstart' in div && 'ondrop' in div) && 'FormData' in window && 'FileReader' in window;
    }();

    // Comment modal
    $('.comment-btn').on('click', openCommentModal);
    function openCommentModal() {
        var post = $(this).data('post');

        var $cmtModal = $('#comment-modal');
        $cmtModal.find('.comment-form').data('post', post);
        $cmtModal.find('.comment-text').val('');

        $cmtModal.modal('show');
    }

    $('.comment-form').on('submit', sendComment);
    function sendComment(e) {
        e.preventDefault();

        var $cmtModal = $('#comment-modal');
        var $form = $cmtModal.find('.comment-form');
        var post = $form.data('post');
        var text = $form.find('.comment-text').val();

        axios.post('/comment', {
            post: post,
            text: text
        }).then(function (res) {
            console.log(res);
            $cmtModal.modal('hide');
        }).catch(function (err) {
            console.log(err);
        });
    }

    // Message modal
    $('.msg-btn').on('click', openMsgModal);
    function openMsgModal() {
        var user = $(this).data('user');

        var $msgModal = $('#message-modal');
        $msgModal.find('.message-form').data('user', user);
        $msgModal.find('.message-text').val('');

        $msgModal.modal('show');
    }

    // Send message
    $('.message-form').on('submit', sendMessage);
    function sendMessage(e) {
        e.preventDefault();

        var $msgModal = $('#message-modal');
        var $form = $msgModal.find('.message-form');
        var user = $form.data('user');
        var text = $form.find('.message-text').val();

        axios.post('/message', {
            user: user,
            text: text
        }).then(function (res) {
            console.log(res);
            $msgModal.modal('hide');
        }).catch(function (err) {
            console.log(err);
        });
    }

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
        var $postModal = $('#post-modal');
        $postModal.find('.post-form').data('action', '/post');
        $postModal.find('.modal-title').text('New Post');
        $postModal.find('.submit-btn').text('Submit');
        $postModal.find('.text').val('');
        $postModal.find('.tags').val('');
        $postModal.find('.file').val('');
        $postModal.find('.url').val('');
        $postModal.find('.preview').empty();

        openPostModal();
    }

    // Open post modal for editing
    function openEditModal(post) {
        var $postModal = $('#post-modal');
        $postModal.find('.post-form').data('action', '/post/edit/' + post.id);
        $postModal.find('.modal-title').text('Edit Post');
        $postModal.find('.submit-btn').text('Save Changes');
        $postModal.find('.text').val(post.text);
        $postModal.find('.tags').val(post.tags.join(', '));
        $postModal.find('.file').val('');
        $postModal.find('.url').val('');

        var $preview = $postModal.find('.preview');
        $preview.empty();

        openPostModal(post.images);
    }

    // Post modal
    function openPostModal(images) {
        var $postModal = $('#post-modal');

        var $form = $postModal.find('.post-form');
        var $text = $postModal.find('.text');
        var $tags = $postModal.find('.tags');
        var $preview = $postModal.find('.preview');
        var $url = $postModal.find('.url');
        $url.on('input', function (e) {
            uploadImageURL($url.val());
        });
        var $file = $postModal.find('.file');
        $file.change(function (e) {
            handleFiles(e.currentTarget.files);
        });
        var $submitBtn = $postModal.find('.submit-btn');
        $submitBtn.on('click', submit);

        var $droparea = $postModal.find('.droparea');
        var $dropbox = $postModal.find('.dropbox');
        $dropbox.on('dragenter', dragenter);
        $dropbox.on('dragover', dragover);
        $dropbox.on('dragleave', dragleave);
        $dropbox.on('drop', drop);

        var $switchBtn = $postModal.find('.switch-input');
        $switchBtn.on('click', switchInputs);

        var formData = new FormData();

        // If editing, add post's images and add them to formData
        if (images) {
            images.forEach(function (image) {
                addImage(image.link, 'image-' + image.id);
                formData.set('image-' + image.id, '' + image.id);
            });
        }

        hideLoading();
        $postModal.modal('show');

        function addImage(image, id) {
            $('\n                <div class="image" data-id="' + id + '">\n                    <button type="button" class="remove" data-id="' + id + '">&times;</button>\n                    <img src="' + image + '" />\n                </div>\n            ').appendTo($preview);
            $postModal.find('.remove').on('click', removeImage);
        }

        function removeImage() {
            var imageID = $(this).data('id');
            formData.delete('' + imageID);
            $preview.find('.image[data-id=\'' + imageID + '\']').remove();
        }

        function uploadImageURL(url) {
            if (!$url.val()) return;

            $url.val('');
            showLoading();
            axios.post('/image/url', {
                url: url
            }).then(function (res) {
                var image = res.data.image;
                addImage(image.link, 'image-' + image.id);
                formData.set('image-' + image.id, '' + image.id);
                hideLoading();
            }).catch(function (err) {
                hideLoading();
                console.log(err.response.data);
            });
        }

        function handleFiles(files) {
            $.each(files, function (i, f) {
                var imageID = hashCode(f.name);
                var reader = new FileReader();
                reader.onload = function (e) {
                    addImage(e.target.result, imageID);
                };

                reader.readAsDataURL(f);

                formData.set('' + imageID, f);
            });

            $file.val('');
        }

        function submit() {
            if ($form.hasClass('is-uploading')) return false;

            $form.addClass('is-uploading');
            showLoading();

            formData.set('text', $text.val());
            formData.set('tags', $tags.val());

            var url = $postModal.find('.post-form').data('action');
            axios.post(url, formData).then(function (res) {
                $form.removeClass('is-uploading');
                hideLoading();
                if (res.data.reload) {
                    document.location.reload(true);
                } else if (res.data.redirect) {
                    document.location.assign(res.data.redirect);
                }
            }).catch(function (err) {
                console.log(err);
            });
        }

        function switchInputs() {
            $postModal.find('.url-upload').toggleClass('hide');
            $postModal.find('.file-upload').toggleClass('hide');
            if ($postModal.find('.url-upload').hasClass('hide')) {
                $switchBtn.text('Upload photo by URL');
            } else {
                $switchBtn.text('Upload photo from file');
            }
        }

        function showLoading() {
            $postModal.find('.loading').removeClass('hide');
        }

        function hideLoading() {
            $postModal.find('.loading').addClass('hide');
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
            $droparea.addClass('dragover');
        }

        function dragleave(e) {
            e.stopPropagation();
            e.preventDefault();
            $droparea.removeClass('dragover');
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
            var $confirmModal = $('#confirm-modal');
            if (!!$confirmModal) {
                $confirmModal.find('.modal-title').text(title);
                $confirmModal.find('#text').text(text);

                var $submitBtn = $confirmModal.find('#submit-btn');
                $submitBtn.text(btn);
                $submitBtn.on('click', resolve);

                var cancelBtn = $confirmModal.find('#cancel-btn');
                cancelBtn.on('click', reject);

                $confirmModal.modal({
                    backdrop: 'static',
                    keyboard: false
                });
            } else {
                reject('No confirm modal found');
            }
        });
    }

    // Delete button
    var $deleteBtn = $('.delete-btn');
    if (!!$deleteBtn) {
        $deleteBtn.on('click', function (e) {
            var btn = e.currentTarget;
            var postID = btn.dataset.post;

            askConfirm({ title: 'Delete post?', btn: 'Delete' }).then(function () {
                axios.get('/post/delete/' + postID).then(function (res) {
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

    // Reblog button
    $('.reblog-btn').on('click', reblogPost);
    function reblogPost(e) {
        var postID = $(this).data('post');

        axios.get('/reblog/' + postID).then(function (res) {
            var post = JSON.parse(res.data.post);
            openReblogModal(post);
        }).catch(function (err) {
            console.log(err);
        });
    }

    function openReblogModal(post) {
        var $reblogModal = $('#reblog-modal');
        $reblogModal.find('.reblog-form').attr('action', '/reblog/' + post.id);
        $reblogModal.find('.text').val('');
        $reblogModal.find('.tags').val('');
        var $preview = $reblogModal.find('.preview');
        $preview.empty();

        post.images.forEach(function (image) {
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

    // Utils
    function hashCode(str) {
        var hash = 0;
        if (str.length == 0) return hash;
        for (var i = 0; i < str.length; i++) {
            var char = str.charCodeAt(i);
            hash = (hash << 5) - hash + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return hash;
    }
})(axios);