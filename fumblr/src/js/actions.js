/*
 * actions types
 */

 export const LOAD_POSTS = 'LOAD_POSTS';
 export const GOT_POSTS = 'GOT_POSTS';

 /*
  * action creators
  */

export function loadPosts() {
	return {
		type: LOAD_POSTS
	}
}

export function gotPosts({ post_count, more }) {
	return {
		type: GOT_POSTS,
		more,
		post_count
	}
}
