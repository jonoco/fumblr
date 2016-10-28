import { combineReducers } from 'redux';
import { LOAD_POSTS, GOT_POSTS } from './actions';

const pagesInitialState = { 
	post_count: 0, 
	more: false,
	loading: false 
};

function pages(state = pagesInitialState, action) {
	switch (action.type) {
		case LOAD_POSTS:
			return Object.assign({}, state, {
				loading: true
			});

		case GOT_POSTS:
			return Object.assign({}, state, {
				more: action.more,
				post_count: action.post_count,
				loading: false
			});

		default:
			return state
	}

	return state;
}

const fumblrApp = combineReducers({
	pages
});

export default fumblrApp;