KindEditor.ready(function(K) {
    window.editor = K.create('#id_desc',{
        // 指定大小
        width: '800px',
        height: '450px',
        themeType: 'simple',
        uploadJson: 'api/v1/upload_image?format=json'
    });
});
