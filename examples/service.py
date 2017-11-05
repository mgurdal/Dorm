from dorm import Node, DORM

if __name__ == '__main__':
    label = """  _____     ____    _____    __  __
 |  __ \   / __ \  |  __ \  |  \/  |
 | |  | | | |  | | | |__) | | \  / |
 | |  | | | |  | | |  _  /  | |\/| |
 | |__| | | |__| | | | \ \  | |  | |
 |_____/   \____/  |_|  \_\ |_|  |_|


  ______                                                               _
 |  ____|                                                             | |
 | |__     _ __    __ _   _ __ ___     ___  __      __   ___    _ __  | | __
 |  __|   | '__|  / _` | | '_ ` _ \   / _ \ \ \ /\ / /  / _ \  | '__| | |/ /
 | |      | |    | (_| | | | | | | | |  __/  \ V  V /  | (_) | | |    |   <
 |_|      |_|     \__,_| |_| |_| |_|  \___|   \_/\_/    \___/  |_|    |_|\_\\
    """
    d = DORM()
	#towns = d.find('Towns').select().all()
    node_form = ("Name: ", "IP: ", "Port: ", "User (docker): ", "Password: ", "Database Type: ", "Replica(No): ")
    command = input("""Options:\n\t1. Create Node\n\t""")
    while True:
        if command == "1":
            values = []
            for f in node_form:
