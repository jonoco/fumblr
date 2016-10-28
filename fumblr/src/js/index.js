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

const LOAD_HEIGHT = 1000;

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

    // check for scrolling on pages with posts
    ['gallery', 'dashboard', 'user', 'likes'].forEach(location => {
      if (!!document.getElementById(location))  {
        document.addEventListener('scroll', _.debounce(() => {
            if (getPosition() <= LOAD_HEIGHT && store.getState().pages.more) {
                loadNextPage(location);
            }
        }, 250, { 'maxWait': 500 }));   
      }
    });
    
    function getPosition() {
        return document.body.clientHeight - window.innerHeight - window.scrollY;
    }

    function loadNextPage(location) {
        if (store.getState().pages.loading) return;
        
        store.dispatch(loadPosts());

        let url = `/${location}/posts/${store.getState().pages.post_count}?raw_posts=1`;
        if (location === 'user') {
            url = `${window.location.pathname}/posts/${store.getState().pages.post_count}?raw_posts=1`;
        }

        axios.get(url)
        .then(res => {
            $(res.data.posts).appendTo('.post-list');
            store.dispatch(gotPosts(res.data.state.pages));
        }).catch(err => {
            console.log(err.message);
        });
    }

    let unsubscribe = store.subscribe(handleChange);
    function handleChange() {
        const list = $('.post-list');
        if (store.getState().pages.loading && !$('.post-loading').length) {
            $(`<div class="post-loading">
                <i class="fa fa-refresh fa-spin fa-3x fa-fw"></i>
                </div>`).appendTo(list);
        } else {
            $('.post-loading').remove();
        }

        if (!store.getState().pages.more) {
            unsubscribe();
        }
    }

}());