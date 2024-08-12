#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from pathlib import Path
import os
import TradeTide

root_path = Path(TradeTide.__path__[0])

repository = Path(root_path)

data = repository / 'data'

usd_eur = eur_usd = data.joinpath('eur_usd')
