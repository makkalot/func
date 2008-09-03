#!/sbin/runscript

depend() {
	need net
}

start() {
	ebegin "Starting funcd"
	start-stop-daemon --start --background --make-pidfile \
	                  --pidfile /var/run/funcd.pid   \
			  --exec /usr/bin/funcd
	eend $? "Failed to start funcd"
}

stop() {
	ebegin "Stopping funcd"
	start-stop-daemon --stop --quiet --pidfile /var/run/funcd.pid
	eend $? "Failed to stop funcd"
}

