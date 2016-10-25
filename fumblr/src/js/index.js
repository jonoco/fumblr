import axios from 'axios';
import PostModal from './post-modal';
import { askConfirm } from './confirm-modal';
import LightBox from './lightbox';
import Header from './header';
import Messages from './messages';
import Comment from './comment';
import './post';
import { stopScrolling } from './utils';

(function() {
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

}());