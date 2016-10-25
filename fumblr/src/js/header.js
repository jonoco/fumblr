import { stopScrolling } from './utils';

export default class Header {
	constructor() {
		this.$mobileHeader = $('.mobile-header');

		$('#header').find('.menu-btn, .mask').on('click', this.toggleSideMenu);

		this.$mobileHeader.find('.search-btn').on('click', this.openMobileSearch.bind(this));
		this.$mobileHeader.find('.close-btn').on('click', this.closeMobileSearch.bind(this));
		this.$mobileHeader.find('form').on('submit', this.closeMobileSearch.bind(this));
	}	

	openMobileSearch() {
		this.$mobileHeader.addClass('open-search');
		this.$mobileHeader.find('input').focus();
	}

	closeMobileSearch() {
		this.$mobileHeader.removeClass('open-search');
	}

	toggleSideMenu() {
		window.scrollTo(0,0);
		$('#header').toggleClass('open-menu');
		$('.menu-btn').toggleClass('fa-bars').toggleClass('fa-close');
		stopScrolling($('#header').hasClass('open-menu'));
	}
}
