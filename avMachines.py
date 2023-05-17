
import subprocess

# Machine names
with open('Machines.txt','r') as file:
    machine_Names = list(filter(None,file.read().splitlines()))


machine_Names=set(machine_Names)

Machine_Dispo=[]
for Name in machine_Names:
    try:
        result=subprocess.check_output(["ssh", Name, 'exit'], stderr=subprocess.PIPE)
        Machine_Dispo.append(Name)
    except:
        continue


with open('Machine_file', 'w') as file:
    file.write("\n".join(Machine_Dispo))
