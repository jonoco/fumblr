import axios from 'axios';
import PostModal from './post-modal';
import { askConfirm } from './confirm-modal';
import LightBox from './lightbox';
import Header from './header';
import Messages from './messages';
import Comment from './comment';
import './post';
import { stopScrolling } from './utils';
import { createStore } from 'redux';
import fumblrApp from './reducers';
import { loadPosts, gotPosts } from './actions';
import _ from 'lodash';

(function() {
    let store = createStore(fumblrApp, window.STATE_FROM_SERVER);

    // Check browser compatibility for form support
    const isAdvancedUpload = function() {
      const div = document.createElement('div');
      return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) 
        && 'FormData' in window && 'FileReader' in window;
    }();

    function checkAdvancedUpload() {
        if (!isAdvancedUpload) {
            alert(`advanced upload not supported: 
                FormData| ${'FormData' in window}
                FileReader| ${'FileReader' in window}`);
        } else {
            alert(`supporting advanced upload: 
                FormData| ${'FormData' in window}
                FileReader| ${'FileReader' in window}`);
        }
    }

    const postModal = new PostModal();
    const lightbox = new LightBox();
    const header = new Header();
    const messages = new Messages();
    const comment = new Comment();

    // Follow button
    $('.follow-btn').on('click', followUser);
    function followUser(e) {
        const $btn = $(this);
        const user = $btn.data('user');

        axios.post('/follow', {
            user
        }).then(res => {
            if (res.data.follow) {
                $btn.toggleClass('following');    
            } else {
                document.location.assign(res.request.responseURL);
            }
            
        }).catch(err => {
            console.log(err);
        });
    }

    const gallery = document.getElementById('gallery');
    if (!!gallery) {
        document.addEventListener('scroll', () => { checkPosition() });   
    }

    const checkPosition = _.debounce(_checkPosition, 250, { 'maxWait': 500 });
    function _checkPosition() {
        const LOAD_HEIGHT = 1000;
        if (getPosition() <= LOAD_HEIGHT) {
            loadNextPage();
        }
    }
    
    function getPosition() {
        return document.body.clientHeight - window.innerHeight -  window.scrollY;
    }

    function loadNextPage() {
        if (store.getState().pages.loading) return;
        if (!store.getState().pages.more) {
            console.log('there are no more posts to get');
        }
        
        store.dispatch(loadPosts());

        axios.get(`/gallery/${store.getState().pages.post_count}?json=1`)
        .then(res => {
            $(res.data.posts).appendTo('#gallery .gallery-wrap');
            store.dispatch(gotPosts(res.data.state.pages));
            
        }).catch(err => {
            console.log(err.message);
        })
    }

}());