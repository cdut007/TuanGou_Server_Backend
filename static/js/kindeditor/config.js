KindEditor.ready(function(K) {
    window.editor = K.create('#id_desc',{
        // 指定大小
        width: '800px',
        height: '450px',
        themeType: 'simple',
        allowFileManager: true,
        formatUploadUrl: false,
        fileManagerJson: 'http://192.168.239.129:8000/api/v1/file_manager?format=json',
        uploadJson: 'http://'+ window.location.host + '/api/v1/upload_image?format=json'
    });
});
