(function(){

    // Search bar
    const searchBar = document.querySelector('#search-bar');
    searchBar.addEventListener('submit', search);

    function search(e) {
        console.log(e);
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