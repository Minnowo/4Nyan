


# this is used to change the ports
# this file modifies the other files and changes the port number to the vluae in config/ports.json
# not the best idea, but it should work well enough if you do want to change them off the default.

# also this doesn't change the firewall rule ports, so you're gonna have to change the firewall.bat files 

if __name__ == "__main__":

    import os 
    import sys 
    import json 
    from re import compile, IGNORECASE
    from tkinter import messagebox

    CONFIG_PATH   = "..\\config\\ports.json"
    FRONTEND_PATH = "..\\frontend\\client\\package.json"
    BACKEND_PATH  = "..\\backend\\main.py"

    # looking for this:
    # uvicorn.run(app, host="0.0.0.0", port=721)
    MATCH_BACKEND  = compile(r"^\s*uvicorn\s*\.\s*run\s*\(.*port\s*\=\s*(\d+).*$", flags=IGNORECASE)
    SUB_BACKEND    = compile(r"port\s*\=\s*(\d+)")

    # error checking
    if not os.path.isfile(CONFIG_PATH):
        messagebox.showerror(title="set_ports.py FATAL", message="The path {0} does not exist. The ports cannot be set.".format(CONFIG_PATH))
        sys.exit()

    if not os.path.isfile(FRONTEND_PATH):
        messagebox.showerror(title="set_ports.py FATAL", message="The path {0} does not exist. The ports cannot be set.".format(FRONTEND_PATH))
        sys.exit()

    if not os.path.isfile(BACKEND_PATH):
        messagebox.showerror(title="set_ports.py FATAL", message="The path {0} does not exist. The ports cannot be set.".format(BACKEND_PATH))
        sys.exit()


    # get ports 
    ports = {}
    with open(CONFIG_PATH, "r") as reader:

        ports = json.load(reader)


    frontend_port = ports.get("frontend", 722)
    backend_port = ports.get("backend", 721)


    # read frontend
    with open(FRONTEND_PATH, "r") as front_reader:

        front = json.load(front_reader)

        front["scripts"]["start"] = "set PORT={0} && react-scripts start".format(str(frontend_port))

    # write frontend
    with open(FRONTEND_PATH, "w") as front_writer:
        
        json.dump(front, front_writer, indent=3)



    # read backend
    lines = []

    with open(BACKEND_PATH, "r") as back_reader:

        for line in back_reader:

            m = MATCH_BACKEND.search(line)

            if not m:
                lines.append(line)
                continue 
            
            lines.append(SUB_BACKEND.sub("port=" + str(backend_port), line))

    # write backend
    with open(BACKEND_PATH, "w") as back_writer:

        for line in lines:
            back_writer.write(line)
