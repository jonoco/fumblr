import _ from 'lodash';
import { stopScrolling } from './utils';

export default class LightBox {
	constructor() {
		this.$lightbox = $('#lightbox');
		this.$image = this.$lightbox.find('img');
		this.$mask = this.$lightbox.find('.lightbox-mask');

		$('.post .images img').on('click', this.openImage.bind(this));
		this.$lightbox.on('click', this.hideLightbox.bind(this));
	}

	openImage(e) {
		const link = $(e.currentTarget).attr('src');
		this.$image.attr('src', link);

		this.showLightbox();
	}

	hideLightbox() {
		stopScrolling(false);
		this.$lightbox.addClass('hide');
	}

	showLightbox() {
		stopScrolling(true);
		this.$lightbox.removeClass('hide');		
	}
}