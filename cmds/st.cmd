# This should be a test or example startup script

require vat616

iocshLoad(${vat616_DIR}/vat616_server.iocsh, "IOCNAME = ioc-vat616, IP_ADDR = 192.168.10.117")

iocshLoad(${vat616_DIR}/vat616_valve.iocsh, "PREFIX=CstatV-RHtr, V=CV580, INDX=0")
iocshLoad(${vat616_DIR}/vat616_valve.iocsh, "PREFIX=CstatV-RHtr, V=CV581, INDX=1")
iocshLoad(${vat616_DIR}/vat616_valve.iocsh, "PREFIX=CstatV-RHtr, V=CV582, INDX=2")
iocshLoad(${vat616_DIR}/vat616_valve.iocsh, "PREFIX=CstatV-RHtr, V=CV583, INDX=3")
