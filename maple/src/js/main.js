(function(){

    const likeButton = document.querySelector('#like-btn');
    likeButton.addEventListener('click', e => {
        const postID = e.currentTarget.dataset.post;

        axios.post('/like', {
            post: postID
        }).then(res => {
            likeButton.classList.toggle('btn-success');
        }).catch(err => {
            console.log(err);
        });
    });    

}(axios))