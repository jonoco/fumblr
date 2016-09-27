(function(){

    // Post Button
    $('.post-btn').on('click', openPostModal);

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

    // Open post modal for editing
    function openEditModal(post) {
        const postModal = $('#post-modal');
              postModal.find('.modal-title').text('Edit Post');
              postModal.find('.submit-btn').text('Save Changes');
              postModal.find('.text').val(post.text);
              postModal.find('.tags').val(post.tags.join(', '));
              postModal.find('.post-form').attr('action', `/post/edit/${post.id}`);
        
        const preview = postModal.find('.preview');
        const img = $('<img class="image" />');
              img.attr('src', post.link);
              img.appendTo(preview);
     
        openPostModal();
    }
    
    // Post modal
    function openPostModal() {
        const postModal = $('#post-modal');

        const form = postModal.find('.post-form');
        const text = postModal.find('.text');
        const tags = postModal.find('.tags');
        const preview = postModal.find('.preview');
        const file = postModal.find('.photo');
            file.change(e => {
                handleFiles(e.currentTarget.files);
            });
        const submitBtn = postModal.find('.submit-btn');
              submitBtn.on('click', submit);
        
        const droparea = postModal.find('.droparea');
        const dropbox = postModal.find('.dropbox');
              dropbox.on('dragenter', dragenter);
              dropbox.on('dragover', dragover);
              dropbox.on('dragleave', dragleave);
              dropbox.on('drop', drop);

        postModal.modal('show');

        function addPreviewImage(src) {
            preview.empty();
            const img = $('<img class="image" />');
            img.attr('src', src);
            img.appendTo(preview);
        }

        function handleFiles(files) {
            preview.empty();
            const img = $('<img class="image" />');

            const reader = new FileReader();
            reader.onload = (function (aImg) { 
                return function (e) { aImg.attr('src', e.target.result); }; 
            })(img);
            reader.readAsDataURL(files[0]);

            img.appendTo(preview);
        }

        function submit() {
            form.submit();
        }

        function drop(e) {
            e.stopPropagation();
            e.preventDefault();

            var files = e.originalEvent.dataTransfer.files;
            
            file.files = files;
            console.log(file.files);

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
    function askConfirm({ text='Are you sure you want to do that?', title='Are you sure?', btn='Confirm' }) {
        return new Promise(function(resolve, reject){
            const confirmModal = $('#confirm-modal');
            if (!!confirmModal) {
                confirmModal.find('.modal-title').text(title);
                confirmModal.find('#text').text(text);
                
                const submitBtn = confirmModal.find('#submit-btn');
                submitBtn.text(btn);
                submitBtn.on('click', resolve);

                const cancelBtn = confirmModal.find('#cancel-btn');
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
    const deleteBtn = $('.delete-btn');
    if (!!deleteBtn) {
        deleteBtn.on('click', (e) => {
            const btn = e.currentTarget;
            const postID = btn.dataset.post;

            askConfirm({ title: 'Delete post?', btn: 'Delete' })
            .then(() => {
                axios.get(`/post/delete/${postID}`)
                .then(res => {
                    console.log(res);
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
            console.log(res.data.following);
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