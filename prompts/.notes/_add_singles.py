# -*- coding: utf-8 -*-
import json, os
path = 'seasons/01-xianxia/chronicle/_STUB_MANIFEST.json'
manifest = json.load(open(path, encoding='utf-8'))
files = set(manifest.get('files', []))
names_to_add = [
    'ch791-林崇看.md','ch835-林叙等.md','ch844-林彻看林夙.md','ch855-林叙等.md',
    'ch856-林崇信.md','ch858-林彻站.md','ch859-苏挽在.md','ch860-林叙看.md',
    'ch861-林崇看.md','ch862-灶边.md','ch863-苏挽端糖.md','ch864-林彻看林夙.md',
    'ch871-林崇看.md','ch872-灶边.md','ch875-林叙等.md','ch876-林崇信.md',
    'ch877-灶边雪.md','ch878-林彻站.md','ch879-苏挽在.md','ch880-林叙看.md',
    'ch883-苏挽端糖.md','ch884-林彻看林夙.md','ch887-灶边雪.md','ch888-林彻站.md',
    'ch892-灶边.md','ch895-林叙等.md','ch896-林崇信.md','ch899-苏挽在.md',
    'ch900-林叙看.md','ch901-林崇看.md','ch903-苏挽端糖.md','ch904-林彻看林夙.md',
    'ch907-灶边雪.md','ch908-林彻站.md','ch912-灶边.md','ch915-林叙等.md',
    'ch916-林崇信.md','ch919-苏挽在.md','ch920-林叙看.md','ch921-林崇看.md',
    'ch923-苏挽端糖.md','ch924-林彻看林夙.md','ch927-灶边雪.md','ch928-林彻站.md',
    'ch932-灶边.md','ch935-林叙等.md','ch936-林崇信.md','ch939-苏挽在.md',
    'ch940-林叙看.md','ch941-林崇看.md','ch943-苏挽端糖.md','ch944-林彻看林夙.md',
    'ch946-林崇信.md','ch947-灶边雪.md','ch948-林彻站.md','ch952-灶边.md',
    'ch955-林叙等.md','ch956-林崇信.md','ch959-苏挽在.md','ch960-林叙看.md',
    'ch961-林崇看.md','ch963-苏挽端糖.md','ch964-林彻看林夙.md','ch967-灶边雪.md',
    'ch968-林彻站.md','ch972-灶边.md','ch975-林叙等.md','ch976-林崇信.md',
    'ch979-苏挽在.md','ch980-林叙看.md','ch981-林崇看.md','ch983-苏挽端糖.md',
    'ch984-林彻看林夙.md','ch987-灶边雪.md','ch988-林彻站.md','ch992-灶边.md',
    'ch995-林叙等.md','ch996-林崇信.md',
]
added = 0
for n in names_to_add:
    if n not in files:
        files.add(n)
        added += 1
manifest['files'] = sorted(files)
with open(path, 'w', encoding='utf-8') as fh:
    fh.write(json.dumps(manifest, ensure_ascii=False, indent=2))
print('added', added, 'filenames. total manifest files:', len(manifest['files']))
