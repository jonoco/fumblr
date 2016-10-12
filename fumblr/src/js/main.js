(function(){
    
    // View messages
    $('.message-user').on('click', openUserMessages);
    function openUserMessages(e) {
        const user = $(this).addClass('selected').data('user');
        $(`.message-user[data-user!='${user}']`).removeClass('selected')
        $(`.user-messages[data-user!='${user}']`).addClass('hide');
        const msgList = $(`.user-messages[data-user='${user}']`).removeClass('hide');
    }

    // Check browser compatibility for form support
    const isAdvancedUpload = function() {
      const div = document.createElement('div');
      return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) 
        && 'FormData' in window && 'FileReader' in window;
    }();
    
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
            console.log(res);
            $cmtModal.modal('hide');
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

    // Post Button
    $('.post-btn').on('click', openUploadModal);

    // Edit Button
    $('.edit-btn').on('click', editPost);

    function editPost() {
        const postID = $(this).data('post');
        
        axios.get(`/post/edit/${postID}`)
        .then(res => {
            const post = JSON.parse(res.data.post);
            openEditModal(post);
        })
        .catch(err => {
            console.log(err)
        });
    }

    // Open post modal for uploading
    function openUploadModal() {
        const $postModal = $('#post-modal');
              $postModal.find('.post-form').attr('action', `/post`);
              $postModal.find('.modal-title').text('New Post');
              $postModal.find('.submit-btn').text('Submit');
              $postModal.find('.text').val('');
              $postModal.find('.tags').val('');
              $postModal.find('.preview').empty();

        openPostModal();
    }

    // Open post modal for editing
    function openEditModal(post) {
        const $postModal = $('#post-modal');
              $postModal.find('.post-form').attr('action', `/post/edit/${post.id}`);
              $postModal.find('.modal-title').text('Edit Post');
              $postModal.find('.submit-btn').text('Save Changes');
              $postModal.find('.text').val(post.text);
              $postModal.find('.tags').val(post.tags.join(', '));
        
        const $preview = $postModal.find('.preview');
              $preview.empty();

        const $img = $('<img class="image" />');
              $img.attr('src', post.link);
              $img.appendTo($preview);
     
        openPostModal();
    }
    
    // Post modal
    function openPostModal() {
        const $postModal = $('#post-modal');

        const $form = $postModal.find('.post-form');
        const $text = $postModal.find('.text');
        const $tags = $postModal.find('.tags');
        const $preview = $postModal.find('.preview');
        const $file = $postModal.find('.photo');
            $file.change(e => {
                handleFiles(e.currentTarget.files);
            });
        const $submitBtn = $postModal.find('.submit-btn');
              $submitBtn.on('click', submit);
        
        const $droparea = $postModal.find('.droparea');
        const $dropbox = $postModal.find('.dropbox');
              $dropbox.on('dragenter', dragenter);
              $dropbox.on('dragover', dragover);
              $dropbox.on('dragleave', dragleave);
              $dropbox.on('drop', drop);

        const formData = new FormData();

        $postModal.modal('show');

        function addPreviewImage(files) {
            $preview.empty();
            const img = $('<img class="image" />');

            const reader = new FileReader();
            reader.onload = (function (aImg) { 
                return function (e) { aImg.attr('src', e.target.result); }; 
            })(img);
            reader.readAsDataURL(files[0]);

            img.appendTo($preview);
        }

        function handleFiles(files) {
            addPreviewImage(files);

            $.each( files, (i, f) => {
                formData.set( 'file', f );
            });
        }

        function submit() {
            if ($form.hasClass('is-uploading')) return false;

            $form.addClass('is-uploading');
            formData.set('text', $text.val());
            formData.set('tags', $tags.val());

            const url = $postModal.find('.post-form').attr('action'); 

            axios.post(url, formData)
            .then( res => {
                $form.removeClass('is-uploading');
                if (res.data.reload) {
                    document.location.reload(true);
                } else if (res.data.redirect) {
                    document.location.assign(res.data.redirect);
                }
            })
            .catch( err => {
                console.log(err);
            });
        }

        function drop(e) {
            e.stopPropagation();
            e.preventDefault();

            const files = e.originalEvent.dataTransfer.files;
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
    function askConfirm({ text='Are you sure you want to do that?', title='Are you sure?', btn='Confirm' }) {
        return new Promise(function(resolve, reject){
            const $confirmModal = $('#confirm-modal');
            if (!!$confirmModal) {
                $confirmModal.find('.modal-title').text(title);
                $confirmModal.find('#text').text(text);
                
                const $submitBtn = $confirmModal.find('#submit-btn');
                $submitBtn.text(btn);
                $submitBtn.on('click', resolve);

                const cancelBtn = $confirmModal.find('#cancel-btn');
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
    const followButtons = document.querySelectorAll('.follow-btn');
    if (!!followButtons) {
        followButtons.forEach(btn => {
            btn.addEventListener('click', followUser);
        });
    }
    function followUser(e) {
        const btn = e.currentTarget;
        const user = btn.dataset.user;

        axios.post('/follow', {
            user
        }).then(res => {
            btn.classList.toggle('following')
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
            btn.classList.toggle('liked');
        }).catch(err => {
            console.log(err);
        });
    }    

}(axios))