export default class Header {
	constructor() {
		this.$mobileHeader = $('.mobile-header');

		this.$mobileHeader.find('.search-btn').on('click', this.openMobileSearch.bind(this));
		this.$mobileHeader.find('.close-btn').on('click', this.closeMobileSearch.bind(this));
		this.$mobileHeader.find('form').on('submit', this.closeMobileSearch.bind(this));
	}	

	openMobileSearch() {
		this.$mobileHeader.find('.nav-icons').addClass('hide-top');	
		this.$mobileHeader.find('.search-bar').removeClass('hide-top');	
		this.$mobileHeader.find('input').focus();
	}

	closeMobileSearch() {
		this.$mobileHeader.find('.nav-icons').removeClass('hide-top');	
		this.$mobileHeader.find('.search-bar').addClass('hide-top');	
	}
}
