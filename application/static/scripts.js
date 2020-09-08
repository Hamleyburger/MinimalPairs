// Makes file names of chosen files show in file input fields given the right label
$(document).ready(function () {
    $('input[type="file"]').change(function (e) {
        var fileName = e.target.files[0].name;
        $('.file-label-name').html(fileName);
        //alert('The file "' + fileName + '" has been selected.');
    });
});
