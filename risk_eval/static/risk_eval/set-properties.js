const setInitialRequired = ($select1, $select2, val) => {
    /* Makes select2 required if select1 value matches val */
    $select1.val() === val ? $select2.prop('required', true) : $select2.prop('required', false);
}

const setRequiredIfMatch = ($select1, $select2, val) => {
    /* Sets the required property of select2 based on the the value
        of select1. If select1 value is val then required is set
        to true */
        setInitialRequired($select1, $select2, val);
        $select1.change(() => {
            $select1.val() === val ? $select2.prop('required', true) : $select2.prop('required', false);
        });
}

const requireDateSelects = () => {
    /* Making all date Selects required for form submission. */
    var $dateSelects = $('select').filter(function() {
        return this.name.match(/_date_/);
    });

    $.each($dateSelects, function() {
        var $this = $(this);
        $this.prop('required', true);
    });
}