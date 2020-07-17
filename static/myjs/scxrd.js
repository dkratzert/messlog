$(document).ready(function () {

    var polyglot = new Polyglot({
        locale: 'de',
        phrases: {
            "Number": "Nummer",
            "Project Name": "Projektname",
            "Date Measured": "Messdatum",
            "Machine": "Maschine",
            "Operator": "Operator",
            "Publ.": "publiz.",
            "CIF": "CIF",
            "Edit": "ändern",
        }
    });

    // some options for JSmol_lite:
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
        //keys: true,
        renderer: 'bootstrap4',
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
                title: polyglot.t("Number"),
                name: 'number',
                searchable: false,
                orderable: true,
            },
            {
                title: polyglot.t("Project Name"),
                name: 'experiment_name',
                searchable: true,
                orderable: true,
            },
            {
                title: polyglot.t("Date Measured"),
                name: 'measure_date',
                searchable: false,
                orderable: true,
            },
            {
                title: polyglot.t("Machine"),
                name: 'machine',
                searchable: false,
                orderable: true,
            },
            {
                title: polyglot.t("Operator"),
                name: 'operator',
                searchable: false,
                orderable: true,
            },
            {
                title: polyglot.t("Publ."),
                name: 'publishable',
                searchable: false,
                orderable: true,
            },
            {
                title: polyglot.t('CIF'),
                name: 'cif_file_on_disk',
                visible: true,
                searchable: false,
                orderable: true,
                render: function (d) {
                    if (d === '') {
                        // A svg check mark:
                        return '';
                    } else {
                        return '<svg class="bi bi-check" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">\n' +
                            '<path fill-rule="evenodd" d="M13.854 3.646a.5.5 0 010 .708l-7 7a.5.5 0 01-.708 0l-3.5-3.5a.5.5 0 11.708-.708L6.5 10.293l6.646-6.647a.5.5 0 01.708 0z" clip-rule="evenodd"/>\n' +
                            '</svg>';
                    }
                },
            },
            {
                title: polyglot.t('Edit'),
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
        // console.log(tdata);
        var tab_url = 'table/' + tdata[0];
        cif_file = tdata[7];
        measurement_id = tdata[0];
        // Load the details table for the respective measurements:
        $.get(url = tab_url, function (result) {
            //console.log(result);
            document.getElementById("ttable").innerHTML = result;
        });
        get_mol_and_display();
        //row0.removeClass('selected');
    });

    /* //Trying keyboard navigation:
    dtable.on('key-focus', function() {
      $('#exptable').DataTable().row(getRowIdx()).select();
      console.log('selected', getRowIdx())
    })

    function getRowIdx() {
        return $('#exptable').DataTable().cell({
            focused: true
        }).index().row;
    }*/

    dtable.ajax.reload(function (json) {
        var row = $('#exptable tbody tr:eq(0)');
        //row.addClass("selected");
        row.click();
    });

    function get_mol_and_display() {
        $.post(
            url = 'molecule/',
            data = {
                cif_file: cif_file,
                measurement_id: measurement_id,
                grow: grow_struct,
                'csrfmiddlewaretoken': csrftoken
            },
            function (result) {
                if (result.toString().startsWith('<svg', 0)) {
                    console.log('replacing');
                    document.getElementById("molcard").innerHTML = result.toString();
                } else {
                    console.log('jmol');
                    display_molecule(result);
                }
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

    // Go to initial state on page reload or, because otherwise the collapsible state of the not_measured_cause 
    // field is in opposite state what it should be. An alternative would be to set a cookie.
    var box = document.getElementById('measure_check');
    if (box !== null) {
        box.removeAttribute('checked');
    }
});
