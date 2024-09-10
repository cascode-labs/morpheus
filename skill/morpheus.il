procedure(Morph_onData()

print("data")

)

procedure(Morph_onError()

print("error")

)

procedure(Morph_onFinish()

print("finish")

)



procedure( CCSmorpheusDataTrig( argList )
let(( cellName file libId objId viewFileName viewName viewType )
    cellName = argList->cellName
    libId = argList->libId
    viewName = argList->viewName
    viewType = argList->viewType
    viewFileName = ddMapGetViewTypeFileName( viewType )

    if( objId = ddGetObj( libId~>name cellName viewName viewFileName nil "r" )
;; Existing view open code
      then
       ; file = ddGetObjWritePath( objId )
        println("existing view")
;; New view creation code
    else
    ; Create the firefox cellView
    objId = ddGetObj( libId~>name cellName viewName viewFileName nil "w" )
    file = ddGetObjWritePath( objId )
    
    system(sprintf(nil "touch %s" file))
    )
    start_gui()
)
)
procedure( CCSmorpheusAppTrig(argL) t )
procedure( CCSmorpheusEnableTrig(@optional argL) t )

procedure( CCSmorpheusRegister()
  deRegApp(
    ?appName "morpheus"
    ?appTrigger 'CCSmorpheusAppTrig ; Dummy function
    ?dataTrigger 'CCSmorpheusDataTrig
    ?enableTrigger 'CCSmorpheusEnableTrig ; Dummy function
    ?viewType "morpheus"
    ?widgetType "none"
  )
)
;; Below code handles automatic filling of view naming
;viewVal = envGetVal("graphic" "viewNameToTypeList")
;newViewVal = strcat(viewVal ", firefox firefox_url")
;envSetVal("graphic" "viewNameToTypeList" 'string newViewVal)

CCSmorpheusRegister()


procedure(morpheus_kill()
ipcKillProcess(morpheus.ipc)
morpheus.ipc = nil
)

;procedure(morpheus()

;)


        procedure(start_gui()
            let((USER PROJ)

            USER = getShellEnvVar("USER")
            PROJ = getShellEnvVar("PROJ")
            id = strcat(PROJ,"_",USER) ; ID FOR PROJECT (MAY NEED MORE FOR )
            pyStartServer(?id id) ;Need to set the id
            load_user_config()
            run_command = sprintf(nil,"%s/bin/morpheus --id %s &",morpheus_location, id)
            print(run_command)
            morpheus.ipc = ipcBeginProcess(run_command "" 'Morph_onData 'Morph_onError 'Morph_onFinish pyStartServer.logName)
            
            ;RunTerminalGui(run_command "Starting Morpheus GUI")
            )
        )
            procedure(load_user_config()

                prt=infile("~/.morpheus/user.sysm.yml")
                morpheus_location= ""
                gets(text, prt)
                while(text != nil
                    pattern = pcreCompile("morpheus-location: \"(.*)\"")
                    match = pcreExecute(pattern text)
                    if(match == t then 
                        morpheus_location = pcreSubstitute(pattern "\\1")
                        )
                

                    gets(text, prt) ;get next text
                )
                print(morpheus_location)
            )
        procedure(RunTerminalGui(command @optional (title "running command") "tt")
            "Opens a terminal and runs the specified command.  It will give it the specified title"
            system(strcat(
            "gnome-terminal --window -t \"" title "\""
            " -e \"tcsh -c \\\"" command 
            " && echo '\\nPress any key to close'"
            " && read\\\"\""))
        )

        procedure(CCSrunUnixScript( commandName scriptPath @optional (outputFile 
        "default.txt") (options "")(displayFile nil) "ttgg" )
            let(( runCommand msgHandler errHandler childId ip nextline)
                if(isFile(scriptPath) == t then
                    if(isExecutable(scriptPath) == t then
                        runCommand = strcat(commandName " " scriptPath " > " 
                        outputFile "" options )
                        printf("Running Unix/Linux command\n$prompt> %s\n" runCommand)
                        msgHandler = lambda( (cid data) printf("\n[Msg 
                        CCSrunUnixScript: %s]\n%s" cid data))
                        errHandler = lambda( (cid data) printf("\n[Err 
                        CCSrunUnixScript: %s]\n%s" cid data))
                        childId = ipcBeginProcess(runCommand "" 'msgHandler 
                        'errHandler)
                        ipcWait(childId)
                        if(displayFile == t then
                            view(outputFile)
                        else
                            ip=infile(outputFile)
                            when(ip
                                while( gets(nextline ip)
                                    printf("%L\n" car(parseString(nextline "\n")))
                                ) ;while
                            )
                            close(ip) 
                            t
                        )
                        else
                        warn("Input Script %s doesn't have Executable 
                        Permissions.\n" scriptPath)
                    ); if
                    else
                      warn("Input Script %s doesn't exist in system.\n" scriptPath)
                )
            )
        )
