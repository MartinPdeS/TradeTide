#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from pathlib import Path
import os
import TradeTide

root_path = Path(TradeTide.__path__[0])

cwd = os.getcwd()

repository = Path(cwd)

data = repository / 'TradeTide' / 'TradeTide' / 'data'

usd_eur = eur_usd = data.joinpath('eur_usd')