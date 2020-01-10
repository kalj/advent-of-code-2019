#!/usr/bin/env python3

import sys

class Deck:
    def __init__(self,ncards):
        self.size = ncards
        self.cards = list(range(ncards))

    def __str__(self):
        return ' '.join('{:2d}'.format(n) for n in self.cards)

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

class SingleIndexDeck:

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

class ExpressionDeck:
    def __init__(self,ncards):
        self.size = ncards
        self.a = 1
        self.b = 0

    def card_at_index(self,k):
        return (self.a*k+self.b)%self.size

    def __str__(self):
        return ' '.join('{:2d}'.format(self.card_at_index(k)) for k in range(self.size))

    def cut(self,cutsize):
        if cutsize < 0:
            cutsize += self.size
        self.b = (self.b+self.a*cutsize)%self.size

    def deal_into_new(self):
        self.b = (self.b+self.a*(self.size-1))%self.size
        self.a = -self.a

    def deal_with_increment(self,increment):
        for i in range(increment):
            c = self.size*i+1
            if c%increment == 0:
                factor = c//increment
                break
        self.a = (self.a*factor)%self.size

    def inverse_deal_with_increment(self,increment):
        self.cards,olddeck = [0]*self.size,self.cards
        for i in range(self.size):
            self.cards[i] = olddeck[(i*increment)%self.size]

    def index_of_card(self,card):
        return [i for i in range(self.size) if self.card_at_index(i)==card][0]



def shuffle_deck(deck,commands,do_log_print=False):
    if do_log_print:
        print(deck)
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
        if do_log_print:
            print(deck)

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

def do_part1(lines):
    print('## Part 1')
    print()
    decksize = 10007

    # deck = Deck(decksize)
    deck = SingleIndexDeck(decksize,2019)
    # deck = ExpressionDeck(decksize)

    # print("Initially:",deck)

    shuffle_deck(deck,lines)
    # print("Result:",deck)

    idx2019 = deck.index_of_card(2019)
    print("Index of 2019:",idx2019)
    print()

def verify_inverse(lines):
    print("## Verifying inverse")
    print()
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

    print("SingleIndexDeck")

    deck = SingleIndexDeck(decksize,7)
    print("Initially:",deck)

    shuffle_deck(deck,lines_s4)
    print("After shuffle:",deck)
    shuffle_deck(deck,revlines_s4)
    print("After inverse shuffle:",deck)
    print()


def expt_rec(a, b, mod):
    if b == 0:
        return 1
    elif b % 2 == 1:
        return (a * expt_rec(a, b - 1,mod))%mod
    else:
        p = expt_rec(a, b / 2,mod)
        return (p * p)%mod

def geom_sum_rec(a,n,mod):
    if n == 0:
        return 1
    elif n == 1:
        return (1+a)%mod
    elif n%2==0:
        last_term = expt_rec(a,n,mod)
        return (geom_sum_rec(a,n-1,mod)+last_term)%mod
    else:
        smaller = geom_sum_rec((a*a)%mod,(n-1)//2,mod)
        return ((1+a)*smaller)%mod

def do_part2(lines):
    print('## Part 2')
    print()

    decksize = 119315717514047
    nshuffles = 101741582076661

    deck = ExpressionDeck(decksize)
    shuffle_deck(deck,lines)

    a = deck.a
    b = deck.b

    a_final = expt_rec(a,nshuffles,decksize)
    b_final = geom_sum_rec(a,nshuffles-1,decksize)
    b_final = (b*b_final)%decksize

    deck.a = a_final
    deck.b = b_final

    print("Done! Card[2020]={}".format(deck.card_at_index(2020)))

if len(sys.argv) >= 2:

    lines = open(sys.argv[1]).read().splitlines()

    decksize = 25
    if len(sys.argv) > 2:
        decksize = int(sys.argv[2])

    if len(sys.argv) > 3 and sys.argv[3]=='expr':
        deck = ExpressionDeck(decksize)
    else:
        deck = Deck(decksize)

    shuffle_deck(deck,lines,do_log_print=True)

else:

    lines = open('input').read().splitlines()

    do_part1(lines)

    verify_inverse(lines)

    do_part2(lines)
