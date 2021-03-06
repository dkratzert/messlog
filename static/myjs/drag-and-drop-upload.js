function get_uploaded_files(upload_files) {
    console.log(upload_files);
    $.get(url = upload_files, function (result) {
        console.log(result);
        document.getElementById("upload_here").innerHTML = result;
    });
}

$(function () {

    $(".js-upload-files").click(function () {
        $("#fileupload").click();
    });

    $("#fileupload").fileupload({
        dataType: 'json',
        sequentialUploads: true,  /* 1. SEND THE FILES ONE BY ONE */
        start: function (e) {  /* 2. WHEN THE UPLOADING PROCESS STARTS, SHOW THE MODAL */
            /*$("#modal-progress").modal("show");*/
        },
        stop: function (e) {  /* 3. WHEN THE UPLOADING PROCESS FINNISHED, HIDE THE MODAL */
            /* But only hide if modal sends the shown signal */
            /*
            $('#modal-progress').on('shown.bs.modal', function () {
                $('#modal-progress').modal('hide');
            });
            */
        },
        progressall: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
            var progress = parseInt(data.loaded / data.total * 100, 10);
            var strProgress = progress + "%";
            var bar = $(".progress-bar");
            bar.css({"width": strProgress});
            bar.text(strProgress);
        },
        done: function (e, data) {
            /*
            if (data.result.is_valid) {
                $("#gallery tbody").prepend(
                    "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
                );

                var bar = $(".progress-bar");
                bar.css({"width": '0%'});
                bar.text('0%');

                 $('#progress_upload').hide();
            }
            */
            get_uploaded_files(upload_files);
        }

    });

});
