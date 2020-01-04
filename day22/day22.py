#!/usr/bin/env python3

import sys

class Deck:
    def __init__(self,ncards):
        self.size = ncards
        self.cards = list(range(ncards))

    def __str__(self):
        return ' '.join(str(n) for n in self.cards)

    def cut(self,cutsize):
        self.cards = self.cards[cutsize:]+self.cards[:cutsize]

    def deal_into_new(self):
        self.cards.reverse()

    def deal_with_increment(self,increment):
        self.cards,olddeck = [0]*self.size,self.cards
        for i in range(self.size):
            self.cards[(i*increment)%self.size] = olddeck[i]

    def inverse_deal_with_increment(self,increment):
        self.cards,olddeck = [0]*self.size,self.cards
        for i in range(self.size):
            self.cards[i] = olddeck[(i*increment)%self.size]

    def index_of_card(self,card):
        return [i for i,c in enumerate(self.cards) if c==card][0]

    def card_at_index(self,idx):
        return self.cards[idx]

class FakeDeck:

    def __init__(self,ncards,card_of_interest):
        self.size = ncards
        self.teh_card = card_of_interest
        self.card_pos = self.teh_card

    def __str__(self):
        s = ""
        if self.card_pos > 0:
            s += '... '
        s += "{} (idx={})".format(self.teh_card,self.card_pos)
        if self.card_pos < (self.size-1):
            s += ' ...'
        return s

    def cut(self,cutsize):

        cutsize = cutsize % self.size # convert to positive
        if self.card_pos < cutsize:
            self.card_pos += self.size-cutsize
        else:
            self.card_pos -= cutsize

    def deal_into_new(self):
        self.card_pos = (self.size-1)-self.card_pos

    def deal_with_increment(self,increment):
        self.card_pos = (self.card_pos*increment)%self.size

    def inverse_deal_with_increment(self,increment):
        self.card_pos = [(self.card_pos+self.size*i)//increment for i in range(increment) if (self.card_pos+self.size*i)%increment == 0][0]

    def index_of_card(self,card):
        if card != self.teh_card:
            raise Exception("Cannot query for anything but card {} ({} was asked for)".format(self.teh_card,card))

        return self.card_pos

    def card_at_index(self,idx):
        if idx != self.card_pos:
            raise Exception("Cannot query for any position but {} ({} was asked for)".format(self.card_pos,idx))
        return self.teh_card

def shuffle_deck(deck,commands):
    for line in commands:
        # print('{:24s} ->'.format(line),' '.join(str(n) for n in deck))

        command = line.split()
        if command[0] == 'cut':
            cutsize = int(command[1])
            deck.cut(cutsize)

        elif line == 'deal into new stack':
            deck.deal_into_new()

        elif ' '.join(command[:-1]) == 'deal with increment':
            increment = int(command[-1])
            deck.deal_with_increment(increment)

        elif ' '.join(command[:-1]) == 'inverse deal with increment':
            increment = int(command[-1])
            deck.inverse_deal_with_increment(increment)
        else:
            raise Exception("Unknown shuffle instruction: {}".format(line))
        # print('{:24s} ->'.format(''),' '.join(str(n) for n in deck))

def inverse_commands(commands):
    rev_commands = []

    for line in reversed(commands):
        command = line.split()
        if command[0] == 'cut':
            cutsize = int(command[1])
            rev_commands.append('cut {}'.format(-cutsize))

        elif line == 'deal into new stack':
            rev_commands.append(line)

        elif ' '.join(command[:-1]) == 'deal with increment':
            increment = int(command[-1])
            rev_commands.append('inverse '+line)

        elif ' '.join(command[:-1]) == 'inverse deal with increment':
            increment = int(command[-1])
            rev_commands.append(' '.join(command[1:]))
    return rev_commands


if len(sys.argv) != 2:
    print("Insufficient arguments!")
    sys.exit(1)

lines = open(sys.argv[1]).read().splitlines()

print()
print('## Part 1')
print()
decksize = 10007

deck = Deck(decksize)
# deck = FakeDeck(decksize,2019)

# print("Initially:",deck)

shuffle_deck(deck,lines)
# print("Result:",deck)

idx2019 = deck.index_of_card(2019)
print("Index of 2019:",idx2019)


if False:
    print()
    print('## Part ?')
    print()
    print("Verifying inverse")
    lines_s4 = open('sample4').read().splitlines()
    revlines_s4 = inverse_commands(lines_s4)

    print("commands:")
    for l in lines_s4:
        print(l)
    print("inverse commands:")
    for l in revlines_s4:
        print(l)
    decksize = 10

    deck = Deck(decksize)
    print("Initially:",deck)

    shuffle_deck(deck,lines_s4)
    print("After shuffle:",deck)
    shuffle_deck(deck,revlines_s4)
    print("After inverse shuffle:",deck)

    print("FakeDeck")

    deck = FakeDeck(decksize,7)
    print("Initially:",deck)

    shuffle_deck(deck,lines_s4)
    print("After shuffle:",deck)
    shuffle_deck(deck,revlines_s4)
    print("After inverse shuffle:",deck)

print()
print('## Part 2')
print()

decksize = 119315717514047
nshuffles = 101741582076661

revlines = inverse_commands(lines)
deck = FakeDeck(decksize,2019)

print("Initially:",deck)

for n in range(nshuffles):
    shuffle_deck(deck,revlines)
    idx2019 = deck.index_of_card(2019)
    if n % 10000 == 0:
        print("Shuffle {}: idx={}".format(n,idx2019))
    if idx2019 == 2019:
        print('BINGO! ... after {} steps'.format(n))

print("Result:",deck)
