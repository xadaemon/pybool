#!/usr/bin/env python3

from pybool.logic import *


def test_repr():
    assert Logic.false.__repr__() == "0"
    assert Logic.true.__repr__() == "1"
    assert Logic.x.__repr__() == "x"
    assert Logic.hz.__repr__() == "high_z"
    assert Logic.lz.__repr__() == "low_z"

def test_ops():
    assert ~Ltrue == Lfalse
    assert ~Lfalse == Ltrue
    assert Ltrue & Ltrue == Ltrue
    assert Ltrue & Lfalse == Lfalse
    assert Ltrue | Lfalse == Ltrue
    assert Lfalse | Lfalse == Lfalse
    assert Ltrue ^ Ltrue == Lfalse


