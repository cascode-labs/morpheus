    x = 0
	y = 0
	maxX = 800
	promptWidth = 200
	height = 30
	width = 650


;fieldList=list(
;    list(
;        hiCreateCyclicField(
;        ?name       'TestCyclic
;        ?prompt		"Options"
;        ?value		"hi"
    ;     ?choices    list("hi" "hello" "world")
    ;     ?enabled	t
    ;     ?invisible	nil
    ;     ?callback   (lambda (field scope value)
    ;                            print(value) 
    ;                         )
    ;     )
    ;     25:5+(y++)*height  maxX:height promptWidth
        
    ; )

;);fieldlist

procedure(printHello()
print("hello world")
)

;procedure(waitForCallback()

;ipc = ipcBeginProcess("sleep 10 ; echo hello")
;ipcWaitForProcess(ipc)
;ipcWait(ipc)
;print(ipcReadProcess(ipc))

;dumb wait
;while(callbackVariable != 1
;    
;    );

;)


;buttonLayout_test = list(list('hello "printHello()") list('hello "printHello()") list('Cancel "hiFormCancel(hiGetCurrentForm())"))

;form2=hiCreateAppForm(
;    ?name           'MorpheusForm2
;    ?formTitle      "Morpheus Cadence GUI Test"
;    ?fields 	    list(list('hello "printHello()")
;        list('Load "rdsMaeAddOceanMeasurementCB()")
;        list('Close "hiFormCancel(hiGetCurrentForm())")
;        )
;    ?unmapAfterCB   t
;    ?buttonLayout   buttonLayout_test
;    ?initialSize    floor(maxX*1.2):floor(y*height)
;) ; hi create app form

; hiDisplayForm(form2)




; defun(pyStartServer2 (@key (id "default") (logLevel "INFO") (singleMode nil) (timeout nil) (python "python3") "ttggt")

;             let(((executableWithArgs lsprintf("%s %L %s" pyStartServer.exe id logLevel)))
;                 if(singleMode then
;                     executableWithArgs = strcat(executableWithArgs "--single")
;                 )
;                 if(timeout then
;                     executableWithArgs = lsprintf("%s --timeout %L" executableWithArgs timeout)
;                 )
;                 print("helo world before \n")
;                 print(executableWithArgs)
;                 print("helo worldafter\n")
;                 executableWithArgs = lsprintf("\"%s\" %s" python executableWithArgs)
;                     print(executableWithArgs)
;                 ;pyStartServer.ipc = ipcBeginProcess(executableWithArgs "" '__pyOnData '__pyOnError '__pyOnFinish pyStartServer.logName)
;                 t
;             )
        
;     )

procedure(Morph_onData()

print("data")

)

procedure(Morph_onError()

print("error")

)

procedure(Morph_onFinish()

print("finish")

)



procedure(morpheus_start(morpheusLocation python id)

;defun(pyStartServer (@key (id "default") (logLevel "INFO") (singleMode nil) (timeout nil) (python "python3") "ttggt")
        if(morpheus.ipc then
            fprintf(stderr, "server is already running\n")
            nil
        else
            let(((executableWithArgs lsprintf("cd %s ; %s -m morpheus" morpheusLocation, python )))

                ;if(timeout then
                    executableWithArgs = lsprintf("%s --id %s", executableWithArgs, id) ;RUN GUI

                    ;executableWithArgs = lsprintf("%s --gui" executableWithArgs) ;RUN GUI
                ;)
                print(executableWithArgs)
                morpheus.ipc = ipcBeginProcess(executableWithArgs "" 'Morph_onData 'Morph_onError 'Morph_onFinish pyStartServer.logName)
                t
            )
        )
   ; )

)

procedure(morpheus_kill()
ipcKillProcess(morpheus.ipc)
morpheus.ipc = nil
)