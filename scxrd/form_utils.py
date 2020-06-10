from crispy_forms.layout import ButtonHolder, Submit, HTML

backbutton = """
    <a role="button" class="btn btn-sm btn-outline-secondary float-right my-0 py-0" 
        href="{% url "scxrd:index"%}">Back to start</a>
    """

save_button = ButtonHolder(
    Submit('Save', 'Save', css_class='btn-primary mr-2 ml-0 mb-3'),
    # This cancel button works in combination with the FormActionMixin in views.py
    # the view is redirected to the index page if the request contains 'cancel'
    Submit('cancel', 'Cancel', css_class='btn btn-danger ml-2 mb-3', formnovalidate='formnovalidate'),
    HTML('<br>'),
)

save_button2 = ButtonHolder(
    Submit('Save', 'Save', css_class='btn-primary mr-2'),
    HTML('''<a href="{% url 'scxrd:index' %}" class="btn btn-outline-danger" formnovalidate="formnovalidate">Cancel</a>'''),
    css_class=' ml-3 mb-3'
)


def card(header_title, button=''):
    return HTML('<div class="card w-100 mb-3">  <div class="card-header">{} {}</div>'.format(header_title, button))


jsme_frame = HTML('''<label for="id_sample_name_samp" class="pl-3 pr-3 pt-2 pb-0 mt-1 mb-1 ml-1 requiredField">
                        Desired Compound<span class="asteriskField">*</span></label>
                        <input type="hidden" id="id_desired_struct_samp" value="" name="desired_struct_samp">
                        <script>
                            //this function will be called after the JSME JavaScriptApplet code has been loaded.
                            function jsmeOnLoad() {
                                jsmeApplet = new JSApplet.JSME("jsme_container", "700px", "540px");
                                jsmeApplet.setCallBack("AfterStructureModified", setSmiles);
                            }
                        </script>'''
                  )
