export function askConfirm({ text='Are you sure you want to do that?', title='Are you sure?', btn='Confirm' }) {
    return new Promise(function(resolve, reject){
        const $confirmModal = $('#confirm-modal');
        if (!!$confirmModal) {
            $confirmModal.find('.modal-title').text(title);
            $confirmModal.find('#text').text(text);
            
            const $submitBtn = $confirmModal.find('#submit-btn');
            $submitBtn.text(btn);
            $submitBtn.on('click', resolve);

            const cancelBtn = $confirmModal.find('#cancel-btn');
            cancelBtn.on('click', reject);

            $confirmModal.modal({
                backdrop: 'static',
                keyboard: false
            });
        } else {
            reject('No confirm modal found');
        }   
    });      
}