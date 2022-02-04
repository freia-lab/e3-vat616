# Usage: ncat -l <port_number> -c 'sh vat616sim.sh'
# or
# Usage: nc -l -p <port_number> --sh-exec 'vat616sim.sh'


noerr="0"
errno="5"
syserr="-1"

function cmd_handle {

    if [[ "$cmd" == "L?" ]]; then
	echo "L= 0 0.0 1 1.1 2 2.2 -3 100"

    elif [[ "$cmd" == "R "[0-1] ]]; then
	echo "$cmd $noerr"

    elif [[ "$cmd" == "R "[2-3] ]]; then
	echo "$cmd $syserr"

    else
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

