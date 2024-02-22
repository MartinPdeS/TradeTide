#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from pathlib import Path
import os
import git

cwd = os.getcwd()

repository = git.Repo('.', search_parent_directories=True)

repository = Path(repository.working_tree_dir)

data = repository / 'TradeTide' / 'data'

usd_eur = eur_usd = data.joinpath('eur_usd')
