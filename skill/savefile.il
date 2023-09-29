;start SKILL program for adding firefox view

procedure( morpheusDataTrig( argList )
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
	println("Opening the form")
    Morpheus()
	;CCStrCreateForm(libId~>name cellName viewName)

;; New view creation code
  else
   ; Create the firefox cellView
    Morpheus()
    ;objId = ddGetObj( libId~>name cellName viewName viewFileName nil "w" )
    ;file = ddGetObjWritePath( objId )

;; Touch a dummy file of zero  byte
	;system(sprintf(nil "touch %s" file))
;;    ipcSleep( 2 )
    ;printf( "Created the firefox cellView!\n" )
  	)
  t
  )
) ; CCSfirefoxDataTrig

;
; Dummy trigger functions
;
procedure( morpheusAppTrig(argL) t )
procedure( morpheusEnableTrig(@optional argL) t )

procedure( morpheusRegister()
  deRegApp(
    ?appName "morpheus"
    ?appTrigger 'morpheusAppTrig ; Dummy function
    ?dataTrigger 'morpheusDataTrig
    ?enableTrigger 'morpheusEnableTrig ; Dummy function
    ?viewType "morpheus"
    ?widgetType "none"
  )
)

;
; Register the triggers
;
morpheusRegister()

