KindEditor.ready(function(K) {
    window.editor = K.create('#id_desc',{
        // 指定大小
        width: '800px',
        height: '450px',
        themeType: 'simple',
        allowFileManager: true,
        formatUploadUrl: false,
        formatUrlMode: 'domain',
        fileManagerJson: 'http://'+ window.location.host + '/api/v1/file_manager?format=json',
        uploadJson: 'http://'+ window.location.host + '/api/v1/upload_image?format=json'
    });
});
