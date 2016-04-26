#coding: utf-8

"""
Trieda slúži ako dátová štruktúra. IsiBin predstavuje pole MxN kde M je pocet elektród a N dĺžka signálu.
Viaceré sety vysvietení sú spriemerované, obsahuje priemernú odozvu na každej elektróde.
"""

class IsiBin:

    def __init__(self):
        self.channelsSignalsAveraged = []


