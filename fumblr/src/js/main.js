(function(){

    // Upload modal
    const uploadModal = document.querySelector('#upload-modal');
    if (!!uploadModal) {
        (function() {
            const form = uploadModal.querySelector('#upload-form');
            const droparea = uploadModal.querySelector('.droparea');
            const preview = $('#upload-modal').find('.preview');
            const dropbox = uploadModal.querySelector('#dropbox');
                  dropbox.addEventListener('dragenter', dragenter, false);
                  dropbox.addEventListener('dragover', dragover, false);
                  dropbox.addEventListener('dragleave', dragleave, false);
                  dropbox.addEventListener('drop', drop, false);

            const uploadBtn = uploadModal.querySelector('#submit-btn');
                  uploadBtn.addEventListener('click', upload);
            
            const file = $('#upload-modal').find('#photo');
                file.change(e => {
                    handleFiles(e.currentTarget.files);
                });

            const text = uploadModal.querySelector('#text');
            const tags = uploadModal.querySelector('#tags');

            function upload(e) {
                form.submit()
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
        }())
    }

    // Edit modal
    const editModal = $('#edit-modal');
    if (!!editModal) {
        (function(){
            const file = editModal.find('#photo');
            const text = editModal.find('#text');
            const tags = editModal.find('#tags');
            const submitBtn = editModal.find('#submit-btn');
                  submitBtn.on('click', submitEdit);

            var postID;

            $('.edit-btn').on('click', openPost);

            function openPost(e) {
                const btn = e.currentTarget;
                postID = btn.dataset.post;

                axios.get(`/post/edit/${postID}`)
                    .then(res => {
                        console.log(res);
                        editPost(JSON.parse(res.data.post));
                    })
                    .catch(err => {
                        console.log(err)
                    });
                
                $(editModal).modal('show');
            }

            function editPost(post) {
                // update form fields from the post data received from server
                text.val(post.text);
                tags.val(post.tags.join(', '));
            }

            function submitEdit() {
                const post = {
                    id: postID,
                    text: text.val(),
                    tags: tags.val()
                };
                
                axios.post(`/post/edit/${postID}`, post)
                    .then(res => {
                        console.log(res);
                        document.location.reload(true);
                    })
                    .catch(err => {
                        console.log(err);
                    });
            }
        }())
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