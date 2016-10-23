import axios from 'axios';
import { askConfirm } from './confirm-modal';

export default class Comment {
    constructor() {
        this.$cmtModal = $('#comment-modal');
        this.$form = this.$cmtModal.find('.comment-form');
        this.$form.on('submit', this.sendComment.bind(this));
        
        $('.comment-btn').on('click', this.openCommentModal.bind(this));     

        this.$comments = $('#comments');
        this.$comments.find('.comment').on('click', this.toggleCommentControls.bind(this));
        this.$comments.find('.delete-btn').on('click', this.deleteComment.bind(this));
    }    

    openCommentModal(e) {
        const post = $(e.currentTarget).data('post');

        this.$form.attr('action', `/comment/post/${post}`);
        this.$cmtModal.find('.comment-text').val('');

        this.$cmtModal.modal('show');
    }

    sendComment(e) {
        e.preventDefault();
        
        const url = this.$form.attr('action');
        const text = this.$form.find('.comment-text').val();

        axios.post(url, { 
            text
        }).then(res => {
            if (res.data.comment) {
                this.$cmtModal.modal('hide');    
            } else {
                document.location.assign(res.request.responseURL);
            }
        }).catch(err => {
            console.log(err.message);
        });
    }

    deleteComment(e) {
        const cmtID = $(e.currentTarget).data('id');
        console.log('delete ' + cmtID);

        askConfirm({ title: 'Delete comment?', btn: 'Delete' })
        .then(() => {
            axios.post(`/comment/delete/${cmtID}`)
            .then(res => {
                if (res.data.comment) {
                    document.location.reload(true);
                } else {
                    document.location.assign(res.request.responseURL);
                }
            }).catch(err => {
                console.log(err.message);
            });
        }).catch(() => {
            console.log('delete cancelled');
        });
        
    }

    toggleCommentControls(e) {
        const $comment = $(e.currentTarget);
        const cmtID = $comment.data('id');

        this.$comments.find(`.comment[data-id!='${cmtID}']`).find(`.controls`).addClass('closed');
        $comment.find('.controls').toggleClass('closed');
    }
}