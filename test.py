from filepack import Archive

a = Archive("./archive.tar")

a.add_member("./a.txt")

a.print_members()
