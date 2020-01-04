lines = open('input').read().splitlines()
module_masses = list(map(int,filter(None,lines)))

def module_fuel_pt1(mass):
    fuel = (mass//3-2)
    return fuel

def module_fuel_pt2(mass):
    self_fuel = (mass//3-2)
    if self_fuel <= 0:
        return 0
    else:
        return self_fuel+module_fuel_pt2(self_fuel)


print(sum(map(module_fuel_pt2,module_masses)))
