#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @(#)day14.py
# @author Karl Ljungkvist <k.ljungkvist@gmail.com>

import sys

class ResourceList:
    def __init__(self,*args):
        self.arr = []
        if len(args) > 0:
            self.arr = args[0]

    def __str__(self):
        return ", ".join(["{} {}".format(i[1],i[0]) for i in self.arr])

    def size(self):
        return len(self.arr)

    def get_resource(self, species):
        res = [r for r in self.arr if r[0]==species]
        if len(res) == 1:
            return res[0]
        elif len(res) == 0:
            return None
        else:
            raise Exception("Unexpected number of matches for species {}: {}".format(species, res))

    def remove_resource(self, res):
        existing = self.get_resource(res[0])
        if not existing:
            raise Exception("Failed to remove non-existing resource {}".format(res))
        if existing[1] < res[1]:
            raise Exception("Failed to remove {} units of {}; only {} units existed".format(res[1],res[0],existing[1]))
        if existing[1] == res[1]:
            self.arr.remove(res)
        else:
            existing[1] -= res[1]

    def add_resource(self,res):
        existing = self.get_resource(res[0])
        if existing:
            existing[1] += res[1]
        else:
            self.arr.append(res)

    def get_most_complex(self, complexities):
        res = None
        max_complexity = -1
        for r in self.arr:
            if complexities[r[0]] > max_complexity:
                res = r
                max_complexity = complexities[r[0]]
        return res

    def contains(self, species):
        res = self.get_resource(species)
        return True if res else False

    def by_complexity(self, complexities):
        for res in reversed(sorted(self.arr,key=lambda c:complexities[c[0]])):
            yield res

def parse_resource(s):
    ws = s.split()
    return [ws[1], int(ws[0])]

class Reaction:
    def __init__(self,lhs,rhs):
        self._lhs = lhs
        self._rhs = rhs
    def parse_from_line(line):
        ingredients,result = line.split('=>')
        return Reaction(list(map(parse_resource,ingredients.strip().split(', '))),parse_resource(result.strip()))

    def __str__(self):
        ingredients_list = ', '.join(["{} {}".format(i[1],i[0]) for i in self.lhs()])
        return "{} => {} {}".format(ingredients_list,self.rhs()[1],self.rhs()[0])

    def lhs(self):
        return self._lhs

    def rhs(self):
        return self._rhs

class ReactionList:
    def __init__(self,fname):
        inlines = open(fname).read().splitlines()
        self.arr = [Reaction.parse_from_line(line) for line in inlines]

    def print(self):
        for r in self.arr:
            print(r)

    def get_producing_reaction(self,ingredient):
        matches  = [r for r in self.arr if r.rhs()[0]== ingredient]
        if len(matches) != 1:
            raise Exception('Unexpected number for matches for reactions producing ingredient {}: {}'.format(ingredient,matches))
        return matches[0]

    def get_ingredients_complexity(self):

        complexities = {'ORE':0}
        def fill_ingredient_complexity(ingredient):
            if not ingredient in complexities:
                # get constituents
                constituents = self.get_producing_reaction(ingredient).lhs()
                # compute complexity recursively
                complexities[ingredient] = 1+max([fill_ingredient_complexity(i[0]) for i in constituents])
            return complexities[ingredient]

        fill_ingredient_complexity('FUEL')
        return complexities

class Factory:
    def __init__(self,reactions_file):
        self.reactions = ReactionList(reactions_file)
        self.complexities = self.reactions.get_ingredients_complexity()
        self.resources = ResourceList()


    def print_complexities(self):
        for i in self.complexities:
            print("{}: {}".format(i,self.complexities[i]))


    def get_required_ore(self,quantity):

        constituents = ResourceList()
        constituents.add_resource(quantity)
        while not (constituents.size() == 1 and constituents.contains('ORE')):

            # start with most complex constituent

            constituent = constituents.get_most_complex(self.complexities)

            # print("Resolving constituent {} with complexity {}".format(constituent[0],self.complexities[constituent[0]]))

            r = self.reactions.get_producing_reaction(constituent[0])

            n_needed = constituent[1]
            n_produced = r.rhs()[1]
            n_reactions = 1+(n_needed-1)//n_produced # integer division with rounding up
            constituents.remove_resource(constituent)
            new_constituents = r.lhs()

            for nc in new_constituents:
                constituents.add_resource([nc[0],n_reactions*nc[1]])


        return constituents.get_resource('ORE')[1]

    def produce(self, chemical,lvl=0):

        species,desired_amount = chemical

        if species == 'ORE':
            return False

        react = self.reactions.get_producing_reaction(species)
        # print('{}About to produce {} through reaction {}'.format(' '*(2*lvl), chemical,react))

        produced_amount = react.rhs()[1]
        n_reactions = 1+(desired_amount-1)//produced_amount # integer division with rounding up

        # check constituents
        constituents = ResourceList(react.lhs())

        for const in constituents.by_complexity(self.complexities):
            # print('{}Checking constituent {} with complexity {}...'.format(' '*(2*lvl),const,self.complexities[const[0]]))
            needed_amount = const[1]*n_reactions

            res = self.resources.get_resource(const[0])

            # use any available resource
            if res:
                used_amount = min(res[1],needed_amount)
                needed_amount -= used_amount
                res[1] -= used_amount
                # print('{}Used {} units of available {}'.format(' '*(2*lvl), used_amount,const[0]))

            if needed_amount > 0:
                # we still need to produce
                # print('{}Need to produce {} units of {}'.format(' '*(2*lvl), needed_amount,const[0]))
                success = self.produce([const[0],needed_amount],lvl+1)
                if not success:
                    # print('Failed producing {}.'.format(const[0]))
                    return False

                self.resources.remove_resource([const[0],needed_amount])

        # add newly produced resource
        self.resources.add_resource([species,produced_amount*n_reactions])
        # print('{}Produced {} units of {}.'.format(' '*(2*lvl), produced_amount*n_reactions,species))

        return True

    def produce_max_fuel(self,ore_amount):

        max_ore_per_fuel = factory.get_required_ore(['FUEL',1])
        self.resources.add_resource(['ORE',ore_amount])

        while True:
            ore_amount = self.resources.get_resource('ORE')[1]
            min_fuel = ore_amount//max_ore_per_fuel

            if min_fuel < 100:
                min_fuel = 1

            print("Producing {} fuel...".format(min_fuel))
            print("{} ORE left, producing {} FUEL...".format(ore_amount,min_fuel))
            success = self.produce(['FUEL',min_fuel])
            if not success:
                break
            print("Current resources:", self.resources)
            print()


            # n=0
            # if n % 100000 == 0:
            # print("Current resources:", self.resources)
            # print()
            # n += 1

        fuel = self.resources.get_resource('FUEL')
        if fuel:
            return fuel[1]
        else:
            return None

if len(sys.argv) < 2:
    print('Insufficient arguments')
    sys.exit(1)

factory = Factory(sys.argv[1])

print(" === Reactions ===")
factory.reactions.print()
print()
print(" === Complexities of of ingredients ===")
factory.print_complexities()

required_ore = factory.get_required_ore(['FUEL',1])
print("Required ORE for 1 FUEL:",required_ore)

ore_amount = 1000000000000
# ore_amount = 100000000
fuel_amount = factory.produce_max_fuel(ore_amount)
print("Fuel produced from {} units of ORE: {}".format(ore_amount,fuel_amount))
