    x = 0
	y = 0
	maxX = 800
	promptWidth = 200
	height = 30
	width = 650


fieldList=list(
    list(
        hiCreateCyclicField(
        ?name       'TestCyclic
        ?prompt		"Options"
        ?value		"hi"
        ?choices    list("hi" "hello" "world")
        ?enabled	t
        ?invisible	nil
        ?callback   (lambda (field scope value)
                               print(value) 
                            )
        )
        25:5+(y++)*height  maxX:height promptWidth
        
    )

);fieldlist


form=hiCreateAppForm(
    ?name           'MorpheusForm
    ?formTitle      "Morpheus Cadence GUI Test"
    ?fields 	    fieldList
    ?unmapAfterCB   t
    ?buttonLayout   list('Empty
                    list('Load "rdsMaeAddOceanMeasurementCB()")
                    list('Close "hiFormCancel(hiGetCurrentForm())")
                        )
    ?initialSize    floor(maxX*1.2):floor(y*height)
) ; hi create app form


hiDisplayForm(form)