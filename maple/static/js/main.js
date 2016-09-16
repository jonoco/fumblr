(function(){

    var likeButton = document.querySelector('#like-btn');
    likeButton.addEventListener('click', function(e) {
        var postID = e.currentTarget.dataset.post;

        axios.post('/like', {
            post: postID
        }).then(function(res) {
            console.log(res.data.like);
            likeButton.classList.toggle('btn-success');
        }).catch(function(err) {
            console.log(err);
        });

//        axios.get('/test', {
//                params: {
//                    thing: 'this is the thing'
//                }
//            })
//            .then(function(res) {
//                console.log(res.data.result)
//            })
//
//        axios.post('/testpost', {
//            thing1: 'george',
//            thing2: 'jetson'
//        }).then(function(res) {
//            console.log(res.data.result)
//        })

//        $.getJSON($SCRIPT_ROOT + '/test', {
//            thing: 'this is the thing'
//        }, function(data) {
//            console.log(data.result)
//        });
//        return false;
    });

}(axios))