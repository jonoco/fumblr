(function(){

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
            btn.classList.toggle('btn-success');
        }).catch(err => {
            console.log(err);
        });
    }    

}(axios))