export function hashCode(str) {
    let hash = 0;
    if (str.length == 0) return hash;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}

export function stopScrolling(bool) {
	if (bool) {
		$('body').addClass('stop-scrolling');
		$('body').bind('touchmove', e => { e.preventDefault(); });
	} else {
		$('body').removeClass('stop-scrolling');
		$('body').unbind('touchmove');
	}	
} 