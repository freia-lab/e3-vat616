# Usage: ncat -l <port_number> -c 'sh vat616sim.sh'
# or
# Usage: nc -l -p <port_number> --sh-exec 'vat616sim.sh'


noerr="0"
errno="5"
syserr="-1"
IFS=' '

function cmd_handle {

    if [[ "$cmd" == "L? 0" ]]; then
	echo "L= 0 0 0 1 0.11"

    elif [[ "$cmd" == "L? 1" ]]; then
	echo "L= 1 1 5 1 2.2"

    elif [[ "$cmd" == "L? 2" ]]; then
	echo "L= 2 -1 0 1 3.3"

    elif [[ "$cmd" == "L? 3" ]]; then
	echo "L= 3 0 0 0 4.4"

    elif [[ "$cmd" == "Rem "[0-1] ]]; then
	read c i <<<"$cmd"
	echo "CS $i $noerr"

    elif [[ "$cmd" == "Rem "[2-3] ]]; then
	read c i <<<"$cmd"
	echo "CS $i $syserr"
	
    elif [[ "$cmd" == "Loc "[1-2] ]]; then
	read c i <<<"$cmd"
	echo "CS $i $noerr"

    elif [[ "$cmd" == "Loc "[03] ]]; then
	read c i <<<"$cmd"
	echo "CS $i $noerr"
	
    else
	echo "? $cmd"
        echo -e "`date '+%H%M%S'`\tunknown command '$cmd'" 1>&2
        return
    fi

    echo -e "`date '+%H%M%S'`\tcommand $cmd" 1>&2;
}


while true; do
	read -r cmd;
	test -z "${cmd}" && exit;
	cmd_handle $cmd; 
done

