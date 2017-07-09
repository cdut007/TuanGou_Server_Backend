KindEditor.ready(function(K) {
    window.editor = K.create('#id_desc',{
        // 指定大小
        width: '800px',
        height: '200px',
        themeType: 'simple',
        uploadJson: 'http://192.168.239.129:8000/api/v1/upload_image'
    });
});