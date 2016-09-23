(function(){

    // Upload modal
    const uploadModal = document.querySelector('#upload-modal');
    if (uploadModal) {
        (function(){
            //TODO validate form behavior here
            const data = {}; 
            
            const form = uploadModal.querySelector('#upload-form');
            const droparea = uploadModal.querySelector('.droparea');
            const dropbox = uploadModal.querySelector('#dropbox');
                  dropbox.addEventListener('dragenter', dragenter, false);
                  dropbox.addEventListener('dragover', dragover, false);
                  dropbox.addEventListener('dragleave', dragleave, false);
                  dropbox.addEventListener('drop', drop, false);

            const uploadBtn = uploadModal.querySelector('#upload-btn');
                  uploadBtn.addEventListener('click', upload);
            
            const file = uploadModal.querySelector('#photo');
            const text = uploadModal.querySelector('#text');
            const tags = uploadModal.querySelector('#tags');

            function upload(e) {
                data.text = text.value;
                data.tags = tags.value;
                data.file = file.files[0];

                form.submit()
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
        }())
    }

    // Follow button
    const followButtons = document.querySelectorAll('.follow-btn');
    if (followButtons) {
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
    if (likeButtons) {
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