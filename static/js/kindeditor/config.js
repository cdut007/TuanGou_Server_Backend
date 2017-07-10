KindEditor.ready(function(K) {
    window.editor = K.create('#id_desc',{
        // 指定大小
        width: '800px',
        height: '450px',
        themeType: 'simple',
        uploadJson: 'http://192.168.222.128:3000/api/v1/upload_image?format=json'
    });
});