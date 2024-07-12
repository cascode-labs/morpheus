
procedure(killcadence()
    pyKillServer()
    printf("Goodbye!\n")
    exit()
    nil
)

procedure(checkstatus()
    morpheus_cadence_manager_status
)

procedure(clearstatus()
morpheus_cadence_manager_status = nil
)
procedure(setstatus()
morpheus_cadence_manager_status = t
)