

$(document).ready(function() {
    // some options for JSmol:
    var bgcolor = $(this.body).css("background-color");
    var jsmol_options;
    jsmol_options = {
        //width: 320,
        //height: 300,
        color: bgcolor,
        //color: "0xf0f0f0",
        shadeAtoms: false,
        addSelectionOptions: false,
        use: "HTML5",
        readyFunction: null,
        defaultModel: "",
        bondWidth: 3,
        zoomScaling: 5,
        pinchScaling: 5.0,
        mouseDragFactor: 0.9,
        touchDragFactor: 0.9,
        multipleBondSpacing: 0,
        spinRateX: -0.08,
        spinRateY: 0.05,
        spinFPS: 20,
        spin: false,
        infodiv: false,
        debug: false,
        j2sPath: ".",
        _serverUrl: ''
    };


    var dtable = $('#exptable').DataTable( {
        processing: true,
        serverSide: false,
        select:     true,
        ajax: {
            url: table_url,
            type: "POST",
            headers: { "X-CSRFToken": csrftoken },  // django templates only the html pages
        },
        stateSave: false,
        paging: false,
        scrollY: 350,    // This defines the height of the table!
        columns: [
            { visible: false,
              searchable: false,},
            { title: "Number",
              searchable: false,},
            { title: "Experiment" },
            { title: "Date",
              searchable: false,
              render: function(d) {
              return moment(d).format("DD:MM:YYYY, HH:mm");
              }
            },
            { title: "Machine" },
            //{ title: "cif"},
            {
            mRender: function(data, type, full) {
            return '<a class="badge badge-danger" href=edit/' + full[0] + '>' + 'Edit' + '</a>';
                }
            },
        ],

        //"lengthMenu": [[2, 25, 50, -1], [2, 25, 50, "All"]],
        // No extra menus:
        //dom: '<"top"i><"clear">',
    });


    dtable.on('click', 'tr', function () {
        var data = dtable.row( this ).data();
        var tab_url = 'table/'+data[1];

        $.get(url = tab_url, function (result) {
            //console.log(result);
            document.getElementById("ttable").innerHTML = result;
        });

        $.post(
            url = 'molecule/',
            data = {id: data[0],
                    grow: false,
                    'csrfmiddlewaretoken': csrftoken
                    },
            function (result) {
                display_molecule(result)
        });
    } );

    function display_molecule(molfile) {
        Jmol._document = null;
        Jmol.getTMApplet("jmol", jsmol_options);
        var jsmolcol = $("#molcard");
        jsmolcol.html(jmol._code);
        jmol.__loadModel(molfile);
        //jsmolcol.removeClass('invisible');
    }

});