    
procedure(morpheus_maeAddOceanMeasurement(session)
    
    pattern = pcreCompile("(\\d+)$")
    match = pcreExecute(pattern session)
    sessionNum = pcreSubstitute(pattern "\\1")
    
    axlFormName = strcat("axlOutputsForm" sessionNum)
    axlWidgetName = strcat("axlOutputsWidget" sessionNum)

    _axlOutputsSetupAddOutputByType(get(eval(stringToSymbol(axlFormName)) axlWidgetName) "ocean" "Transient")
)