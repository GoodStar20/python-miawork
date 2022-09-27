 /* Use backticks and ${varname} to use variables in strings */

 function getRealInput(realInputName){
     /* Returns input element when it's name attribtue is specified */
    let $realInput = $(`input[name=${realInputName}]`);
    return $realInput;
 }

function replaceRealInput(realInputName, $realInput, additionalClasses=''){
    /* Hides the real input and returns the fake input */
    let fakeInputName = realInputName.concat('-fake');
    let $fakeInput = $(`<input id=${fakeInputName} class="form-control ${additionalClasses}" type="text" autocomplete="off">`)
    $fakeInput.insertBefore($realInput);
    $realInput.hide();
    return $fakeInput;
}

function matchRealInputClass($realInput, $fakeInput){
    /* Gives fake input is-invalid or is-valid classes if the real input has those classes */
    if ($realInput.hasClass('is-invalid')){
            $fakeInput.addClass('is-invalid');
    }
    if ($realInput.hasClass('is-valid')){
        $fakeInput.addClass('is-valid');
    }  
}

function matchRealInputPlaceholder($realInput, $fakeInput){
    /* Gives fake input the same placeholder as the real input */
    let realInputPlaceholder = $realInput.attr('placeholder');
    if (realInputPlaceholder){
        $fakeInput.attr('placeholder', realInputPlaceholder);
    }
}

function matchRealDisabledProp($realInput, $fakeInput){
    /* The fake input's disabled property will match that of the real input */
    let realInputDisabled = $realInput.prop('disabled');
    if (realInputDisabled){
        $fakeInput.prop('disabled', realInputDisabled);
    }
}

function createCleave($realInput, $fakeInput){
    /* Creates a cleave to format fake input */
    let cleave = new Cleave($fakeInput, {
        numeral: true,
        prefix: '$',
        stripLeadingZeroes: false,
        noImmediatePrefix: true,
        numeralDecimalScale: 0,
        numeralPositiveOnly: true,
        numeralIntegerScale: 10,
        onValueChanged: function (e) {
            let userInput = cleave.getRawValue();
            if (userInput && userInput != '$'){
                userInput = userInput.replace('$','');             
                userInput = parseInt(userInput);
                $realInput.val(userInput);
            }
            else {
                $realInput.val('');
            }
        }
    });   
}

function initiateFakeVal($realInput, $fakeInput){
    /* Gives the fake input it's initial value which is the formatted value of the real input */
    let realInputVal = $realInput.val();
    if (realInputVal == ''){
        $fakeInput.val('');
    } else {
    let formattedVal = new Intl.NumberFormat('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0, style: 'currency', currency: 'USD', currencyDisplay: 'narrowSymbol'}).format(realInputVal);    
    $fakeInput.val(formattedVal);
    }
}

function removeRequired($realInput){
    /* Real Input cannot be required or else there will be an error when it is hidden.
     Django will do form validation instead of required attribute in html. */
    $realInput.prop('required', false);
}

function removePrefixOnUnfocus($fakeInput){
    /* If there is only a dollar sign remove the prefix in the fake input when someone unfocuses */
    $fakeInput.blur(function(){
        if ($fakeInput.val() == '$'){
            $fakeInput.val('')
        }
    })
}

function prepareFakeInput(realInputName, additionalClasses=''){
    /* Prepares a corresponding fake input when given a real input */
    let $realInput = getRealInput(realInputName);
    let $fakeInput = replaceRealInput(realInputName, $realInput, additionalClasses);
    matchRealInputClass($realInput, $fakeInput);
    createCleave($realInput, $fakeInput);
    initiateFakeVal($realInput, $fakeInput);
    removeRequired($realInput);
    matchRealInputPlaceholder($realInput, $fakeInput);
    matchRealDisabledProp($realInput, $fakeInput);
    removePrefixOnUnfocus($fakeInput);
}

function prepareMultiFakeInput(arr, additionalClasses=''){
    /* Prepares corresponding fake inputs when given an array of real inputs */
    for (let i=0; i < arr.length; i++){
        prepareFakeInput(arr[i].name, additionalClasses);
    }
}