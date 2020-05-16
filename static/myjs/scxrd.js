$(document).ready(function () {
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

    var dtable = $('#exptable').DataTable({
        searching: true,
        processing: true,
        serverSide: true,  // without serverside=true, the list is only 10 items long!
        select: true,
        full_row_select: true,
        ajax: {
            url: table_url,
            type: "POST",
            headers: {"X-CSRFToken": csrftoken},  // django templates only the html pages
        },
        stateSave: false,
        deferRender: false,
        //"DisplayLength": 10000,
        "scrollY": "350px",     // This defines the height of the table!
        "scrollCollapse": true,
        "paging": false,
        "order": [[1, "desc"]],
        columns: [
            {  // title and name are important, otherwise the server-side processing does not work.
                title: 'id',
                name: 'id',
                visible: false,
                searchable: false,
                orderable: true,
            },
            {
                title: "Number",
                name: 'number',
                searchable: false,
                orderable: true,
            },
            {
                title: "Experiment",
                name: 'experiment',
                searchable: true,
                orderable: true,
            },
            {
                title: "Date",
                name: 'measure_date',
                searchable: false,
                orderable: true,
            },
            {
                title: "Machine",
                name: 'machine',
                searchable: false,
                orderable: true,
            },
            {
                title: "Operator",
                name: 'operator',
                searchable: false,
                orderable: true,
            },
            {
                title: "Publ.",
                name: 'publishable',
                searchable: false,
                orderable: false,
            },
            {
                title: 'CIF',
                name: 'cif',
                visible: true,
                searchable: false,
                orderable: true,
                /*render: function (d) {
                    if (d === '') {
                        return '';
                    } else {
                        return check;
                    }
                },*/
            },
            {
                title: 'Edit',
                name: 'edit_button',
                searchable: false,
                orderable: false,
            },
        ],
        //"initComplete": function(settings, json) {
        // Do stuff after table init:
        //var row = dtable.row(':first');
        //$(row).addClass('selected');
        //console.log(row.data());
        //}

        //"lengthMenu": [[2, 25, 50, -1], [2, 25, 50, "All"]],
        // No extra menus:
        //dom: '<"top"i><"clear">',
    });


    dtable.on('click', 'tr', function () {
        var row = dtable.row(this);
        //var row0 = $('#exptable tbody tr:eq(0)');
        var tdata = row.data();
        //console.log(tdata);
        var tab_url = 'table/' + tdata[0];
        cif_id = tdata[1];
        // Load the details table for the respective experiment:
        $.get(url = tab_url, function (result) {
            //console.log(result);
            document.getElementById("ttable").innerHTML = result;
        });
        get_mol_and_display();
        //row0.removeClass('selected');
    });

    dtable.ajax.reload(function (json) {
        var row = $('#exptable tbody tr:eq(0)');
        //row.addClass("selected");
        row.click();
    });

    function get_mol_and_display() {
        $.post(
            url = 'molecule/',
            data = {
                cif_id: cif_id,
                grow: grow_struct,
                'csrfmiddlewaretoken': csrftoken
            },
            function (result) {
                display_molecule(result);
            });
    }

    function display_molecule(molfile) {
        Jmol._document = null;
        delete Jmol._tracker;
        Jmol.getTMApplet("jmol", jsmol_options);
        var jsmolcol = $("#molcard");
        jsmolcol.html(jmol._code);
        jmol.__loadModel(molfile);
        //jsmolcol.removeClass('invisible');
    }

    // just to have it initialized:
    display_molecule('');


    $('#growStruct').click(function () {
        var jsmolcol = $("#molcard");
        grow_struct = !!this.checked;
        // Get molecule data and display the molecule:
        get_mol_and_display();
    });


    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });

    // Initialize popover component
    $(function () {
        $('[data-toggle="popover"]').popover()
    });
});
